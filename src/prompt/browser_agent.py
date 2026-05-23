import datetime


def browser_agent_plan_prompt(
    task: str,
    tools: list[str],
    context: dict,
    step_count: int,
    max_steps: int,
) -> str:
    steps_remaining = max_steps - step_count

    page_state = context.get("page_state", {})
    action_log = context.get("action_log", [])
    links = context.get("links", [])

    action_log_str = ""
    for entry in action_log[-5:]:
        act = entry.get("action", {})
        res = entry.get("result", {})
        action_log_str += f"  Step {entry['step']}: {act.get('tool', '')} -> success={res.get('success', 'unknown')}\n"

    links_str = ""
    for link in links[:15]:
        links_str += f"  - {link.get('text', '')}: {link.get('href', '')}\n"

    tools_str = "\n".join(f"  - {t}" for t in sorted(tools))

    return f"""
Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

You are a Browser Agent. Your task is to use a web browser to accomplish the following goal:

TASK: {task}

You have {steps_remaining} steps remaining (out of {max_steps} total).
Use steps wisely — prefer targeted actions over broad exploration.

CURRENT PAGE STATE:
  URL: {page_state.get('url', 'none')}
  Title: {page_state.get('title', 'none')}
  Tab count: {page_state.get('tab_count', 0)}
  Page text length: {page_state.get('text_length', 0)} characters

AVAILABLE TOOLS:
{tools_str}

RECENT ACTION HISTORY:
{action_log_str if action_log_str else "  (no actions taken yet)"}

LINKS ON CURRENT PAGE (top 15):
{links_str if links_str else "  (no links or page not loaded)"}

RULES:
1. Each action counts as ONE step. Plan accordingly.
2. You MUST respond with a JSON object containing an "actions" array and optional "terminate" flag.
3. Each action must have "tool" (tool name) and "params" (dict of parameters).
4. Only use tools from the AVAILABLE TOOLS list above.
5. If the task is complete or cannot be completed, set "terminate": true and "reason" explaining why.
6. Prioritize important actions — you may not have enough steps for everything.
7. Use extract_text to read page content, navigate to find information, click to interact.
8. After extracting needed information, set terminate to return results.

RESPONSE FORMAT (JSON only, no extra text):
```json
{{
  "actions": [
    {{
      "tool": "tool_name",
      "params": {{ "param1": "value1" }}
    }}
  ],
  "terminate": false,
  "reason": ""
}}
```

When done, set terminate to true:
```json
{{
  "actions": [],
  "terminate": true,
  "reason": "Task completed - found required information"
}}
```
"""


def browser_agent_result_prompt(
    task: str,
    collected_data: list[dict],
    benchmark_mode: bool = False,
) -> str:
    data_str = ""
    for i, item in enumerate(collected_data):
        data_str += f"\n[{i+1}] {item.get('title', 'Untitled')}\n"
        data_str += f"    URL: {item.get('url', '')}\n"
        data_str += f"    Summary: {item.get('brief_summary', '')[:300]}\n"

    return f"""
You are a Browser Agent reporting results.

TASK: {task}

COLLECTED INFORMATION:
{data_str if data_str else "No data was collected."}

Please provide a concise summary of what was found, organized by relevance to the task.
Focus on actionable information and key facts.

RESPONSE FORMAT (JSON only):
```json
{{
  "summary": "A concise summary of findings",
  "sources": ["url1", "url2"],
  "task_complete": true
}}
```
"""
