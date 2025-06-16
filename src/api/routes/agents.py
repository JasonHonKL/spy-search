from fastapi import APIRouter, HTTPException
from ..models.schemas import AgentsRequest
from ..core.config import read_config, write_config

router = APIRouter()

@router.get("/get_config")
async def get_config():
    """Get agent configuration - SAME ENDPOINT"""
    config = read_config()
    return {
        "agents": config["agents"],
        "provider": config["provider"],
        "model": config["model"],
    }

@router.post("/agents_selection")
async def select_agent(body: AgentsRequest):
    """Update agent configuration - SAME ENDPOINT"""
    try:
        config = read_config()
        config["agents"] = body.agents
        config["provider"] = body.provider
        config["model"] = body.model
        write_config(config)
        
        return {
            "success": True,
            "agents_received": body.agents,
            "model_received": body.model,
            "provider_received": body.provider,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))