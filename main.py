"""
This is the main function of the agent
"""
from src.agent import Planner, Agent
from src.router import Server, Router

import logging

logger = logging.getLogger(__name__)


async def generate_report(query, planner: Planner, agents: list[Agent]):
    """
    TODO : refactor 
    """
    planner.query = query
    server = Server()

    planner_router = Router(server, planner)
    server.add_router(planner.name, planner_router)

    for agent in agents:
        r = Router(server, agent)

        logger.info(f"adding agent router {agent.name}")

        server.add_router(agent.name, r)
        planner.add_model(agent.name, agent.description)

    server.set_initial_router(planner.name, query)

    report = await server.start(query=query)
    report = report["data"]

    return report

from src.api.app import router  # Import the router with all your routes
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

STEP = 10
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s",
)

# DON'T create a new router here - use the imported one
# router = APIRouter()  # ← Remove this line!

# Create FastAPI app
app = FastAPI(
    title="Your API",
    description="API Documentation", 
    version="1.0.0"
)

# Include the imported router (which has all your routes)
app.include_router(router)

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)