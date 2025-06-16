from fastapi import APIRouter, HTTPException
from ..models.schemas import TitleRequest, AppendRequest
from ..services.message_service import MessageService

router = APIRouter()
message_service = MessageService()

@router.get("/get_titles")
def get_titles():
    """Get all message titles - SAME ENDPOINT"""
    titles = message_service.get_titles()
    return {"titles": titles}

@router.post("/load_message")
def load_message(request: TitleRequest):
    """Load message by title - SAME ENDPOINT"""
    try:
        content = message_service.load_message(request.title)
        return content
    except HTTPException as e:
        raise e

@router.post("/delete_message")
def delete_message(request: TitleRequest):
    """Delete message by title - SAME ENDPOINT"""
    success = message_service.delete_message(request.title)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Message with title '{request.title}' not found"
        )
    
    return {
        "status": "success",
        "message": f"Message with title '{request.title}' deleted"
    }

@router.post("/append_message")
def append_message(request: AppendRequest):
    """Append message - SAME ENDPOINT"""
    try:
        message_service.append_message(request.title, request.message)
        return {
            "status": "success",
            "message": f"Appended message to title '{request.title}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))