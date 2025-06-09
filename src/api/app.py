from fastapi import APIRouter ,UploadFile, File, Form , HTTPException
from fastapi.responses import FileResponse
import json
import os 
import logging
import shutil

logger = logging.getLogger(__name__)

from ..utils import read_config , write_config
from .models.models import AgentsRequest , Message, FolderContent , FolderListResponse , FolderCreateRequest
from ..main import generate_report

from ..agent import Planner
from ..factory import Factory
from ..model import Model

from typing import List, Optional, Dict

router = APIRouter()


@router.get("/get_config")
async def get_config():
    config = read_config()
    return {"agents":config["agents"] , "provider":config["provider"] , "model":config["model"]}


@router.get("/select_folder")
async def select_folder(folder_name: str):
    """
    Change the column db to ./local_files/{the folder here} 
    Return success true
    """
    folder_path = f"./local_files/{folder_name}"

    config = read_config()
    config['db'] = folder_path

    write_config(config)

    logger.info(f"{folder_path}") 
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
        
    return {"success": True, "selected_folder": folder_name}

@router.post("/delete_folder")
async def delete_folder(filepath: str):
    """
    Delete specific folder
    """
    full_path = f"./local_files/{filepath}"
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Folder not found")
        
    try:
        shutil.rmtree(full_path)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/create_folder")
async def create_folder(filepath: FolderCreateRequest):
    try:
        os.makedirs("./local_files/" + filepath.filepath, exist_ok=True)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/folder_list", response_model=FolderListResponse)
async def get_folder():
    """
    Get the folder list in local_files
    Return {
        files: [
            {"foldername": "folder1", "contents": ["file1", "file2"]},
            {"foldername": "folder2", "contents": ["file3", "file4"]}
        ]
    }
    """
    base_path = "./local_files"
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
        
    folder_list = []
    
    try:
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
                # Get list of contents in the folder
                contents = os.listdir(full_path)
                folder_list.append(FolderContent(
                    foldername=item,
                    contents=contents
                ))
                
        return FolderListResponse(files=folder_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    filepath: str = Form(...),
):
    """
    Upload a file to a specific filepath in local_files directory
    """
    try:
        # Construct the full path
        full_path = os.path.join("./local_files", filepath)
        
        # Check if the directory exists
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            raise HTTPException(status_code=404, detail="Directory not found")
            
        # Save the file
        with open(full_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        return {
            "success": True,
            "filename": file.filename,
            "filepath": filepath
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/delete_file")
async def delete_file(filepath: str):
    """
    Delete a specific file from local_files directory
    """
    try:
        # Construct the full path
        full_path = os.path.join("./local_files", filepath)
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        # Check if it's actually a file
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
            
        # Delete the file
        os.remove(full_path)
        
        return {
            "success": True,
            "deleted_file": filepath
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/download_file/{filepath:path}")
async def download_file(filepath: str):
    """
    Download a file from local_files directory
    filepath: path to the file relative to local_files directory
    """
    try:
        # Construct the full path
        full_path = os.path.join("./local_files", filepath)
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        # Check if it's actually a file
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
            
        # Get the filename from the path
        filename = os.path.basename(filepath)
        
        # Return the file as a download
        return FileResponse(
            path=full_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messags_record")
async def get_messages_record():
    """
        Read the message from the db ?  
    """
    pass

@router.post("/agents_selection")
async def select_agent(body: AgentsRequest):
    """
    Read the request
    ==> save it to the config.json
    shouldn't the config save in client side ?
    """
    arr = []
    for a in body.agents:
        arr.append(a)
    config = read_config()
    config["agents"] = arr
    config["provider"] = body.provider
    config["model"] = body.model 
    with open("./config.json", "w") as f:
        json.dump(config, f, indent=4)
    return {"success": True, "agents_received": body.agents , "model_received":body.model , "provider_received":body.provider}


@router.post("/quick/{query}")
async def quick_response_endpoint(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    try:
        messages_list = json.loads(messages)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in messages field"}

    validated_messages = [Message(**msg) for msg in messages_list]

    res = await quick_response_logic(query, validated_messages, files, api)

    file_details = []
    if files:
        for file in files:
            content = await file.read()
            file_details.append({"filename": file.filename, "size": len(content)})

    return {
        "report": res,
        "files_received": file_details,
        "messages_received": [msg.model_dump() for msg in validated_messages],
    }


@router.post("/report/{query}")
async def report(
    query: str,
    messages: str = Form(...),  # JSON string of messages in form-data
    files: Optional[List[UploadFile]] = File(None),
):
    # Parse the messages JSON string to Python list
    logging.info("start generating report")
    try:
        messages_list = json.loads(messages)
    except json.JSONDecodeError:
        logging.error("invalid JSON in messages field")
        return {"error": "Invalid JSON in messages field"}

    # Validate each message dict using Pydantic (optional but recommended)
    validated_messages = [Message(**msg) for msg in messages_list]

    file_details = []
    if files:
        for file in files:
            # TODO clean the local_files 
            content = await file.read()
            file_details.append({"filename": file.filename, "size": len(content)})

    logging.info("loading main ... ")
    r = await main(query, validated_messages)
    return {
        "report": r,
        "files_received": file_details,
        "messages_received": [msg.model_dump() for msg in validated_messages],
    }


"""
    TODO: refactor
"""
config = read_config()
quick_model: Model = Factory.get_model(config["provider"], config["model"])

async def quick_response_logic(
    query: str,
    messages: List[Message],
    files: Optional[List[UploadFile]] = None,
    api: Optional[str] = None,
):
    # Example: call your model's completion method
    res = quick_model.completion(query)
    # You can also process messages or files here if needed
    return res


async def main(query, api: str = None):
    config = read_config()
    logging.info("finish reading config ...")

    m = Factory.get_model(config["provider"], config["model"])
    planner = Planner(m)
    logging.info("creating agents ... ")
    agents = []

    for agent in config["agents"]:
        m = Factory.get_model(config["provider"], config["model"])
        agents.append(Factory.get_agent(agent, m))

    logging.info(f"finish creating {agents}")
    logging.info("generating report ... ")

    r = await generate_report(query, planner, agents)

    logging.info("finish generating report")
    quick_model.messages.append({"role": "assistant", "content": r})
    return r