from fastapi import APIRouter, Form, File, UploadFile, HTTPException , Depends
from typing import List, Optional
import json
import logging
from ..models.schemas import Message
from ..core.config import read_config

from ...factory import Factory
from ...generate_report import generate_report
from ...model import Model
from ...agent import Planner , Agent
from ...browser.duckduckgo import DuckSearch

from ..database.session import get_db   
from ..services.user_service import UserService
from ..auth.auth import get_current_user

from sqlalchemy.orm import sessionmaker, Session
from datetime import date


from ..models.user import User
from ...prompt.quick_search import quick_search_prompt

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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user has enough tokens (5 tokens for report generation)
    if not UserService.check_and_deduct_tokens(db, current_user["email"], 5):
        raise HTTPException(status_code=403, detail="Insufficient tokens. Need 5 tokens for report generation.")
    
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


# In auth.py - add this endpoint
@router.get("/tokens/status")
async def get_token_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's token status"""
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Reset daily tokens if it's a new day
    if user.last_token_reset < date.today():
        user.daily_tokens = 20
        user.last_token_reset = date.today()
        db.commit()
    
    return {
        "daily_tokens_remaining": user.daily_tokens,
        "last_reset": user.last_token_reset
    }
