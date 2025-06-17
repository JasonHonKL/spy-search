from fastapi import APIRouter , Depends
from .routes import files, messages, agents, streaming, misc, auth
from .auth.auth import get_current_user

router = APIRouter()

# Include all route modules
router.include_router(files.router, tags=["files"], dependencies=[Depends(get_current_user)])
router.include_router(messages.router, tags=["messages"], dependencies=[Depends(get_current_user)])
router.include_router(agents.router, tags=["agents"], dependencies=[Depends(get_current_user)])
router.include_router(streaming.router, tags=["streaming"], dependencies=[Depends(get_current_user)])
router.include_router(misc.router, tags=["misc"], dependencies=[Depends(get_current_user)])
router.include_router(auth.router , tags=["auth"])  # Keep auth unprotected
router.include_router(auth.router , tags=["auth"])