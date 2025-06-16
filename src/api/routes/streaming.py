from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json
import asyncio
import logging
from ..models.schemas import Message
from ..core.model_cache import get_user_model
from ..core.config import read_config

router = APIRouter()
logger = logging.getLogger(__name__)

async def stream_data(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    """Stream completion data"""
    session_id = f"session_{asyncio.current_task().get_name()}_{id(asyncio.current_task())}"
    logger.info(f"[{session_id}] start the stream ...")
    
    try:
        # Parse messages
        validated_messages = [Message(**msg) for msg in json.loads(messages)]
        
        needs_search = "search:" in query
        
        # Get user model
        model_task = asyncio.create_task(get_user_model())
        
        # Handle search if needed
        if needs_search:
            async def search_pipeline():
                from ...browser.duckduckgo import DuckSearch
                search_instance = DuckSearch()
                return await asyncio.to_thread(search_instance.search_result, query)
            
            search_task = asyncio.create_task(search_pipeline())
            model, search_result = await asyncio.gather(model_task, search_task)
            
            from ...prompt.quick_search import quick_search_prompt
            prompt = await asyncio.to_thread(quick_search_prompt, query, search_result)
        else:
            model = await model_task
            prompt = query
        
        # Configure model
        user_messages = [] if len(validated_messages) == 1 else validated_messages[:-1].copy()
        model.messages = user_messages
        
        logger.info(f"[{session_id}] Finished creating model")
        logger.info(f"[{session_id}] Finished Prompt preparation, starting completion stream")
        
        # Stream completion
        completion_stream = model.completion_stream(prompt)
        chunk_count = 0
        seen_content = set()
        
        for chunk in completion_stream:
            if chunk and chunk.strip():
                chunk_hash = hash(chunk.strip())
                if chunk_hash not in seen_content:
                    seen_content.add(chunk_hash)
                    chunk_count += 1
                    yield chunk
                    await asyncio.sleep(0)
        
        if chunk_count == 0:
            logger.warning(f"[{session_id}] No chunks received from model")
            yield "No response generated"
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in messages field")
    except Exception as e:
        logger.error(f"[{session_id}] Error in streaming: {str(e)}")
        yield f"Error: {str(e)}"
    finally:
        logger.info(f"[{session_id}] finish the stream")

@router.post("/stream_completion/{query}")
async def stream_response(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    """Stream completion - SAME ENDPOINT"""
    return StreamingResponse(
        stream_data(query, messages, files, api), media_type="text/plain"
    )

async def stream_academic_data(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    """Stream academic data"""
    try:
        messages_list = json.loads(messages)
        validated_messages = [Message(**msg) for msg in messages_list]
        
        model = await get_user_model()
        model.messages = validated_messages[:-1] if len(validated_messages) != 1 else []
        
        # Search arXiv
        from ...browser.duckduckgo import DuckSearch
        from ...prompt.quick_search import quick_search_prompt
        
        search_result = await DuckSearch().search_result("site:arxiv.org" + query)
        prompt = quick_search_prompt(query, search_result)
        
        for chunk in model.completion_stream(prompt):
            yield chunk
            await asyncio.sleep(0)
            
    except Exception as e:
        yield f"Error: {str(e)}"

@router.post("/stream_completion_academic/{query}")
async def stream_response_academic(
    query: str,
    messages: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    api: Optional[str] = Form(None),
):
    """Stream academic completion - SAME ENDPOINT"""
    return StreamingResponse(
        stream_academic_data(query, messages, files, api), media_type="text/plain"
    )
