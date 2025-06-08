from .agent import Agent
from ..tools.notion_controller import NotionController
from ..prompt.notion import notion_plan_prompt

import json
import logging
from collections import deque

logger = logging.getLogger(__name__)

class NotionAgent(Agent):
    """
    Agent for handling Notion operations.
    Uses NotionController to interact with Notion API and follows the same pattern as Search agent.
    """
    def __init__(self, model, notion_client_id="", notion_client_secret="", notion_redirect_uri=""):
        self.model = model
        self.notion = NotionController(
            client_id=notion_client_id,
            client_secret=notion_client_secret,
            redirect_uri=notion_redirect_uri
        )
        self.description = "interact with Notion workspace"
        self.name = "notion"
        self.todo = deque()
        self.results = []

    async def run(self, task: str, data=None) -> str:
        """
        Execute Notion operations based on the task.
        Similar to search agent pattern, uses LLM to plan operations.
        """
        logger.info("NOTION: RUNNING")
        steps = self._plan(task)
        cur_task = 0

        while cur_task < len(self.todo):
            new_task = self.todo[cur_task]
            logger.info(f"new task: {new_task}")
            
            tool = new_task.get('tool', '')
            params = new_task.get('params', {})
            
            result = await self._execute_tool(tool, params)
            if result:
                self.results.append(result)
            
            cur_task += 1

        return {"agent": "planner", "data": self.results, "task": ""}

    def _plan(self, task: str):
        """Plan Notion operations using LLM."""
        prompt = notion_plan_prompt(task, self.todo)
        logger.info(f"task {task}")
        
        response = self.model.completion(prompt)
        logger.info(f"notion response: {response}")
        
        todo_list = json.loads(self._extract_response(response))
        logger.info(todo_list)
        
        for todo in todo_list:
            self.todo.append(todo)
            
        logger.info(f"self.todo in notion: {self.todo}")
        return len(todo_list)

    async def _execute_tool(self, tool: str, params: dict) -> dict:
        """Execute a specific Notion operation."""
        try:
            match tool:
                # Page Operations
                case "create_page":
                    return self.notion.create_page(**params)
                case "retrieve_page":
                    return self.notion.retrieve_page(**params)
                case "update_page_properties":
                    return self.notion.update_page_properties(**params)
                case "archive_page":
                    return self.notion.archive_page(**params)
                
                # Database Operations
                case "create_database":
                    return self.notion.create_database(**params)
                case "retrieve_database":
                    return self.notion.retrieve_database(**params)
                case "query_database":
                    return self.notion.query_database(**params)
                case "update_database_properties":
                    return self.notion.update_database_properties(**params)
                
                # Block Operations
                case "retrieve_block":
                    return self.notion.retrieve_block(**params)
                case "retrieve_block_children":
                    return self.notion.retrieve_block_children(**params)
                case "append_child_blocks":
                    return self.notion.append_child_blocks(**params)
                case "update_block":
                    return self.notion.update_block(**params)
                case "delete_block":
                    return self.notion.delete_block(**params)
                case "upload_file_to_block":
                    return self.notion.upload_file_to_block(**params)
                
                # User Operations
                case "list_users":
                    return self.notion.list_users()
                case "retrieve_user":
                    return self.notion.retrieve_user(**params)
                
                # Search Operations
                case "search":
                    return self.notion.search(**params)
                
                # Comment Operations
                case "create_comment":
                    return self.notion.create_comment(**params)
                case "retrieve_comments":
                    return self.notion.retrieve_comments(**params)
                
                case _:
                    logger.error(f"Unknown tool: {tool}")
                    return {"status": "error", "message": f"Unknown tool: {tool}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool}: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_send_format(self):
        pass

    def get_recv_format(self):
        pass 