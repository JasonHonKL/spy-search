from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from typing import List, Optional
import json
import logging
from ..models.schemas import Message
from ..core.config import read_config

from ...factory import Factory
from ...generate_report import generate_report
from ...model import Model
from ...agent import Planner , Agent

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/quick/{query}")
async def quick_response_endpoint(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    """Quick response endpoint - SAME ENDPOINT"""
    try:
        messages_list = json.loads(messages)
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
            "messages_received": [msg.dict() for msg in validated_messages],
        }
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in messages field"}

@router.post("/report/{query}")
async def report(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
):
    """Generate report - SAME ENDPOINT"""
    logging.info("start generating report")
    try:
        messages_list = json.loads(messages)
        validated_messages = [Message(**msg) for msg in messages_list]
        
        file_details = []
        if files:
            for file in files:
                content = await file.read()
                file_details.append({"filename": file.filename, "size": len(content)})
        
        logging.info("loading main ... ")
        r = await main(query, validated_messages)
        return {
            "report": r,
            "files_received": file_details,
            "messages_received": [msg.dict() for msg in validated_messages],
        }
    except json.JSONDecodeError:
        logging.error("invalid JSON in messages field")
        return {"error": "Invalid JSON in messages field"}

@router.get("/news/{category}")
def get_news(category: str):
    """Get news - SAME ENDPOINT"""
    from ...browser.duckduckgo import DuckSearch
    res = DuckSearch().today_new(category)
    return {"news": res}

@router.get("/messags_record")
async def get_messages_record():
    """Get messages record - SAME ENDPOINT"""
    pass

# Helper functions (keep original logic)
async def quick_response_logic(
    query: str,
    messages: List[Message],
    files: Optional[List[UploadFile]] = None,
    api: Optional[str] = None,
):
    """Quick response logic - original function"""
    config = read_config()
    
    quick_model: Model = Factory.get_model(config["provider"], config["model"])
    quick_model.messages = messages[::-1]
    
    if files != None:
        pass  # TODO use mark it down to convert to text and append into the data arr
    
    from ...browser.duckduckgo import DuckSearch
    from ...prompt.quick_search import quick_search_prompt
    
    search_result = await DuckSearch().search_result(query)
    prompt = quick_search_prompt(query, search_result)
    res = quick_model.completion(prompt)
    return res

async def main(query, api: str = None):
    """Main function - original logic"""
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
    return r