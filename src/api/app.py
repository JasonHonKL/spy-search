from fastapi import APIRouter
from .routes import files, messages, agents, streaming, misc

router = APIRouter()

# Include all route modules
router.include_router(files.router, tags=["files"])
router.include_router(messages.router, tags=["messages"]) 
router.include_router(agents.router, tags=["agents"])
router.include_router(streaming.router, tags=["streaming"])
router.include_router(misc.router, tags=["misc"])
