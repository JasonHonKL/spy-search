from fastapi import APIRouter ,UploadFile, File, Form , HTTPException
from fastapi.responses import FileResponse,StreamingResponse
import json
import os
import logging

logger = logging.getLogger(__name__)

from ..utils import read_config , write_config
from .models.models import (
    AgentsRequest ,
    Message,
    FolderContent ,
    FolderListResponse ,
    FolderCreateRequest ,
    TitleRequest,
    AppendRequest,
)

from .controller.files import (
    extract_text_from_pdf_bytes
)

from ..main import generate_report

from ..agent import Planner
from ..factory import Factory
from ..model import Model

from ..browser.duckduckgo import DuckSearch
from ..prompt.quick_search import quick_search_prompt

from typing import List, Optional, Dict
from .controller.files import (
    select_folder_handler
)

import asyncio

router = APIRouter()
"""
TODO: !!! Refactor is needed
INSANE REALLY NEED REFACTOR BROOO!!!
"""

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
    folder_path = select_folder_handler(folder_name)
    logger.info(f"{folder_path}")
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")

    return {"success": True, "selected_folder": folder_name}


@router.post("/delete_message")
def delete_message(request: TitleRequest):
    title = request.title
    filename = "messages.json"

    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="messages.json file not found")

    with open(filename, "r", encoding="utf-8") as f:
        try:
            messages = json.load(f)
            if not isinstance(messages, list):
                messages = []
        except json.JSONDecodeError:
            messages = []

    new_messages = [msg for msg in messages if msg.get("title", "").strip().lower() != title.strip().lower()]

    if len(new_messages) == len(messages):
        raise HTTPException(status_code=404, detail=f"Message with title '{title}' not found")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(new_messages, f, ensure_ascii=False, indent=4)

    return {"status": "success", "message": f"Message with title '{title}' deleted"}

@router.post("/create_folder")
async def create_folder(filepath: FolderCreateRequest):
    try:
        os.makedirs("./local_files/" + filepath.filepath, exist_ok=True)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/folder_list", response_model=FolderListResponse)
async def get_folder():
    base_path = "./local_files"

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    folder_list = []

    try:
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
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

@router.get("/get_titles")
def get_titles():
    filename = "messages.json"

    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="messages.json file not found")

    with open(filename, "r", encoding="utf-8") as f:
        try:
            messages = json.load(f)
            if not isinstance(messages, list):
                messages = []
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse messages.json")

    titles = [msg.get("title", "") for msg in messages if "title" in msg]

    return {"titles": titles}

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

"""
    Outdated ?
"""
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

    logger.info(validated_messages)
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

async def stream_data(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    try:
        messages_list = json.loads(messages)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in messages field")
    validated_messages = [Message(**msg) for msg in messages_list]

    logger.info(validated_messages)

    config = read_config()

    quick_model: Model = Factory.get_model(config["provider"], config["model"])
    quick_model.messages = validated_messages[:-1] if len(validated_messages) != 1 else []

    search_result = DuckSearch().search_result(query)
    """
        TODO: do embedding here if content is relevant then don't search top 5 content maybe just top 2 content
    """
    prompt = quick_search_prompt(query , search_result)
    # Example: call your model's completion method
    for chunk in quick_model.completion_stream(prompt):
        yield chunk
        await asyncio.sleep(0)

@router.post("/stream_completion/{query}")
async def stream_response(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    return StreamingResponse(stream_data(query , messages , files , api), media_type="text/plain")


async def stream_academic_data(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    try:
        messages_list = json.loads(messages)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in messages field")
    validated_messages = [Message(**msg) for msg in messages_list]

    logger.info(validated_messages)

    config = read_config()

    quick_model: Model = Factory.get_model(config["provider"], config["model"])
    quick_model.messages = validated_messages[:-1] if len(validated_messages) != 1 else []

    if files != None:
        pass # TODO use mark it down to convert to text and append into the data arr

    search_result = DuckSearch().search_result("site:arxiv.org"+query)
    """
        TODO: do embedding here if content is relevant then don't search top 5 content maybe just top 2 content
    """
    prompt = quick_search_prompt(query , search_result)
    # Example: call your model's completion method
    for chunk in quick_model.completion_stream(prompt):
        yield chunk
        await asyncio.sleep(0)


@router.post("/stream_completion_academic/{query}")
async def stream_response_academic(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    return StreamingResponse(stream_data(query , messages , files , api), media_type="text/plain")




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

@router.get("/news/{category}")
def get_news(category:str):
    res = DuckSearch().today_new(category)
    return {"news":res}


@router.post("/load_message")
def load_message(request: TitleRequest):
    title = request.title

    filename = "messages.json"

    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="messages.json file not found")

    with open(filename, "r", encoding="utf-8") as f:
        try:
            messages = json.load(f)
            if not isinstance(messages, list):
                messages = []
        except json.JSONDecodeError:
            messages = []

    for msg in messages:
        if msg.get("title", "").strip().lower() == title.strip().lower():
            content = msg.get("content")
            if isinstance(content, list):
                return content
            elif isinstance(content, dict):
                return [content]
            elif isinstance(content, str):
                return [{"role": msg.get("role", ""), "content": content}]
            else:
                raise HTTPException(status_code=500, detail="Invalid content format")

    raise HTTPException(status_code=404, detail=f"Message with title '{title}' not found")

@router.post("/delete_message")
def delete_message(title: str):
    """
    Delete the message with the specified title from messages.json.
    """
    filename = "messages.json"

    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="messages.json file not found")

    with open(filename, "r", encoding="utf-8") as f:
        try:
            messages = json.load(f)
            if not isinstance(messages, list):
                messages = []
        except json.JSONDecodeError:
            messages = []

    # Filter out messages with the given title
    new_messages = [msg for msg in messages if msg.get("title") != title]

    if len(new_messages) == len(messages):
        # No message found with the given title
        raise HTTPException(status_code=404, detail=f"Message with title '{title}' not found")

    # Save updated list back to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(new_messages, f, ensure_ascii=False, indent=4)

    return {"status": "success", "message": f"Message with title '{title}' deleted"}

@router.post("/append_message")
def append_message(request: AppendRequest):
    message = request.message
    title = request.title
    filename = "messages.json"
    # Load existing messages or start with empty list
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                messages = json.load(f)
                if not isinstance(messages, list):
                    messages = []
            except json.JSONDecodeError:
                messages = []
    else:
        messages = []

    # Find the message with the matching title
    for msg in messages:
        if msg.get("title") == title:
            # Normalize content to list
            content = msg.get("content")
            if isinstance(content, list):
                # Append new message dict
                content.append({"role": message.role, "content": message.content})
            elif isinstance(content, dict):
                # Convert dict to list and append new message
                msg["content"] = [content, {"role": message.role, "content": message.content}]
            elif isinstance(content, str):
                # Convert string content into list of dicts and append new message
                msg["content"] = [
                    {"role": msg.get("role", ""), "content": content},
                    {"role": message.role, "content": message.content}
                ]
            else:
                # Unexpected content format, just replace with list
                msg["content"] = [{"role": message.role, "content": message.content}]
            # Save and return success
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=4)
            return {"status": "success", "message": f"Appended message to title '{title}'"}

    # Title not found, create new entry
    new_message = {
        "title": title,
        "role": message.role,
        "content": [
            {"role": message.role, "content": message.content}
        ]
    }
    messages.append(new_message)

    # Save to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

    return {"status": "success", "message": f"Created new title '{title}' and saved message"}

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
    """
        TODO: don't call this twice
        TODO: streaming
    """
    config = read_config()
    quick_model: Model = Factory.get_model(config["provider"], config["model"])
    quick_model.messages = messages[::-1]

    if files != None:
        pass # TODO use mark it down to convert to text and append into the data arr

    search_result = DuckSearch().search_result(query)
    """
        TODO: do embedding here if content is relevant then don't search top 5 content maybe just top 2 content
    """
    prompt = quick_search_prompt(query , search_result)
    # Example: call your model's completion method
    res = quick_model.completion(prompt)
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
