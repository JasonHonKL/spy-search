"""
Handling configuration
e.g read config & write config
"""

import json


def read_config():
    with open("./config.json", "r") as file:
        content = file.read()
        config = json.loads(content)
    return config


def write_config(config):
    with open("./config.json", "w") as file:
        json.dump(config, file, indent=4)
