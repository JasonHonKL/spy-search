from .agent import Planner, Agent
from .router import Server, Router

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