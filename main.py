import os
from src.api.app import router

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

STEP = 10


import logging


load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s",
)

app = FastAPI()
app.include_router(router)

port = os.getenv("VITE_PORT")
port = port if port is not None else "8080"
origins = [
    f"http://localhost:{port}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
