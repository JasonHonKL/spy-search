from .agent import Agent
from ..model import Model
from ..browser.browser import Browser
from ..prompt.browser_agent import browser_agent_plan_prompt, browser_agent_result_prompt

import logging

logger = logging.getLogger(__name__)

AVAILABLE_TOOLS = [
    "navigate",
    "click",
    "type",
    "scroll",
    "extract_text",
    "extract_html",
    "get_current_url",
    "get_page_title",
    "screenshot",
    "press_key",
    "wait",
    "find_element",
    "find_elements",
    "get_element_text",
    "get_element_attribute",
    "highlight",
    "execute_script",
    "switch_tab",
    "new_tab",
    "go_back",
    "go_forward",
    "get_state",
    "get_links",
]


class BrowserAgent(Agent):
    """
    Browser Agent uses a web browser to perform tasks on web pages.

    Features:
    - Provides a set of browser tools (navigate, click, type, scroll, etc.)
    - Controls number of steps (configurable max_steps)
    - Runs different benchmarks by tracking success metrics
    - Uses LLM to plan and execute sequences of browser actions

    The agent receives a task from the planner, uses the LLM to plan
    a sequence of tool calls, executes them step by step, and returns
    the gathered information back to the planner.
    """

    def __init__(self, model: Model, max_steps: int = 10, headless: bool = True):
        self.model = model
        self.max_steps = max_steps
        self.headless = headless
        self.browser: Browser | None = None
        self.step_count = 0
        self.action_log: list[dict] = []
        self.page_state: dict = {}
        self.collected_data: list[dict] = []

        self.name = "browser-agent"
        self.description = "Use a web browser to navigate, interact with, and extract information from web pages"

    def get_recv_format(self):
        pass

    def get_send_format(self):
        pass

    def set_name(self, name):
        self.name = name

    async def run(self, task: str, data: list | None = None) -> dict:
        """
        Execute a browser-based task.

        Flow:
        1. Start browser
        2. Ask LLM to plan an initial sequence of actions
        3. For each action, execute the corresponding tool
        4. Track page state and step count
        5. After each action, ask LLM if task is done or needs more steps
        6. When done or max_steps reached, return collected data
        """
        logger.info(f"BrowserAgent: starting task '{task}' with max_steps={self.max_steps}")

        self.browser = Browser(headless=self.headless)
        self.step_count = 0
        self.action_log = []
        self.collected_data = data or []

        try:
            return await self._execute_task(task)
        finally:
            self.browser.close()

    async def _execute_task(self, task: str) -> dict:
        """Execute a task with step control and tool-based interaction."""
        initial_state = self.browser.get_state()
        logger.info(f"Browser initial state: {initial_state}")

        while self.step_count < self.max_steps:
            current_state = self._get_agent_context()
            plan = self._plan_next_actions(task, current_state)

            if plan is None:
                logger.info("BrowserAgent: plan returned None, terminating")
                break

            if plan.get("terminate"):
                logger.info(f"BrowserAgent: LLM requested termination: {plan.get('reason', '')}")
                break

            actions = plan.get("actions", [])
            for action in actions:
                if self.step_count >= self.max_steps:
                    logger.info(f"BrowserAgent: max_steps ({self.max_steps}) reached")
                    break

                self.step_count += 1
                result = self._execute_action(action)
                self.action_log.append({
                    "step": self.step_count,
                    "action": action,
                    "result": result,
                })
                logger.info(f"Step {self.step_count}/{self.max_steps}: {action.get('tool')} -> {result.get('success')}")

        final_text = self.browser.extract_text()[:2000]
        self.collected_data.append({
            "title": self.browser.get_page_title(),
            "url": self.browser.get_current_url(),
            "summary": final_text,
            "brief_summary": final_text[:300],
            "keywords": [],
        })

        return {
            "agent": "planner",
            "data": self.collected_data,
            "task": "",
        }

    def _get_agent_context(self) -> dict:
        """Get the current context including page state and action history."""
        return {
            "page_state": self.browser.get_state(),
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "action_log": self.action_log[-5:],
            "links": self.browser.get_links()[:20],
        }

    def _plan_next_actions(self, task: str, context: dict) -> dict | None:
        """Use LLM to plan the next sequence of actions."""
        prompt = browser_agent_plan_prompt(
            task=task,
            tools=AVAILABLE_TOOLS,
            context=context,
            step_count=self.step_count,
            max_steps=self.max_steps,
        )
        response = self.model.completion(prompt)
        logger.info(f"BrowserAgent plan response: {response}")

        parsed = self._extract_response(response)
        if parsed is None:
            logger.warning("BrowserAgent: failed to parse LLM response")
            return {"actions": [], "terminate": True, "reason": "parse_error"}

        if isinstance(parsed, list):
            return {"actions": parsed, "terminate": False}
        elif isinstance(parsed, dict):
            return parsed

        return {"actions": [], "terminate": True, "reason": "unexpected_format"}

    def _execute_action(self, action: dict) -> dict:
        """Execute a single tool action and return the result."""
        tool = action.get("tool", "")
        params = action.get("params", action.get("parameters", {}))

        tool_method = getattr(self.browser, tool, None)
        if tool_method is None:
            return {"success": False, "error": f"Unknown tool: {tool}"}

        try:
            if callable(tool_method):
                if isinstance(params, dict):
                    result = tool_method(**params)
                else:
                    result = tool_method()
                return result if isinstance(result, dict) else {"success": True, "result": str(result)[:1000]}
            else:
                return {"success": False, "error": f"Tool '{tool}' is not callable"}
        except Exception as e:
            logger.error(f"BrowserAgent: tool '{tool}' error: {e}")
            return {"success": False, "error": str(e)}

    def get_benchmark_stats(self) -> dict:
        """Get benchmark statistics from the last run."""
        total_actions = len(self.action_log)
        successful = sum(1 for a in self.action_log if a["result"].get("success"))
        return {
            "total_steps": self.step_count,
            "max_steps": self.max_steps,
            "total_actions": total_actions,
            "successful_actions": successful,
            "success_rate": round(successful / total_actions, 2) if total_actions > 0 else 0,
            "action_log": self.action_log,
            "pages_visited": len(set(
                a["result"].get("url", "")
                for a in self.action_log
                if isinstance(a["result"], dict) and "url" in a["result"]
            )),
        }
