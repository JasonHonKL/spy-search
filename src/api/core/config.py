import json
import os
from typing import Dict, Any

def read_config() -> Dict[str, Any]:
    """Read configuration from file - keeps original function name"""
    config_file = "./config.json"
    if not os.path.exists(config_file):
        return {
            "agents": [],
            "provider": "openai",
            "model": "deepseek-r1:1.5b"
        }
    
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "agents": [],
            "provider": "ollama", 
            "model": "deepseek-r1:1.5b"
        }

def write_config(config: Dict[str, Any]) -> None:
    """Write configuration to file"""
    with open("./config.json", "w") as f:
        json.dump(config, f, indent=4)