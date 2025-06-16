import asyncio
from typing import Dict, Any, Optional
from ..core.config import read_config

# Global model cache to avoid 7+ second model loading
_model_cache: Dict[str, Any] = {}
_config_cache: Optional[Dict[str, Any]] = None
_cache_lock = asyncio.Lock()

async def get_or_create_model():
    """Get cached model or create new one. Eliminates 7+ second model loading delay."""
    global _model_cache, _config_cache, _cache_lock
    
    async with _cache_lock:
        # Load config once and cache it
        if _config_cache is None:
            _config_cache = await asyncio.to_thread(read_config)
        
        # Create cache key
        cache_key = f"{_config_cache['provider']}_{_config_cache['model']}"
        
        # Return cached model if exists
        if cache_key in _model_cache:
            return _model_cache[cache_key]
        
        # Create new model and cache it
        from ...factory import Factory
        model = await asyncio.to_thread(Factory.get_model, _config_cache["provider"], _config_cache["model"])
        _model_cache[cache_key] = model
        
        return model

async def get_user_model():
    """Create a dedicated model instance for user session"""
    model = await get_or_create_model()
    try:
        # Create a fresh model instance
        config = await asyncio.to_thread(read_config)
        from ...factory import Factory
        user_model = await asyncio.to_thread(Factory.get_model, config["provider"], config["model"])
        return user_model
    except:
        # Fallback: use the cached model
        return model
