from typing import Dict


def report_prompt(query, data) -> str:
    return f"""
    You are provided with the following dataset:

    {data}

    Please carefully analyze the data and answer the following query if the data is relevant:

    Query: {query}

    Requirements:
    - Provide a clear, detailed, and high-quality response.
    - Always include citations referencing the relevant parts of the data.
    - If the data is insufficient or irrelevant to answer the query, state so explicitly.
    - Use professional and precise language.

    Generate the response accordingly.
"""


def report_plan(query: str, short_summaries: Dict[str, str]) -> str:
    return f"""
        You have been given the following problem to address: {query}

        Your task is to write a comprehensive report that provides the user with a full understanding of this issue.

        To assist you, your supervisor has provided a large collection of materials, summarized briefly below. You may reference these summaries at any time to ensure your report is up-to-date and well-informed:

        {short_summaries}

        Your immediate task is to create a detailed plan for the report, specifying which sections will draw upon which parts of the provided summaries.

        Please follow these guidelines:
        - Plan the tasks in the order they should appear in the final report, as the report will be constructed by sequentially appending each section.
        - Clearly indicate which summary tags you will use as citations for each section, as referencing these sources strengthens the report.
        - There could be multiple referral
        - Make sure the plan is detail enough for complex problem, concise enough for easy problem.
        - You plan at the same time should be a good structure, think how to plan your writing as a professional writter.

        Respond with a JSON array in the following format:

        ```json
        [
        {{
            "task": "<description of the section or task>",
            "data": ["<corresponding short summary tag(s)>" , "" ] ,
            "content": "<leave this empty for now>"
        }}
        ]
        ```
        """


def report_task(tasks, task, source):
    return f"""
        You are a report writer. Here is your current list of tasks:
        {tasks}

        Today, you are focusing on the following task:
        {task}

        You have been provided with the following sources:
        {source}

        Please note:
        - Properly cite all sources so that the origin of the content is clear.
        - Your response should include:

        Instruction:
        - The full content will be added directly to the report.
        - Avoid repeating what has already been summarized in previous reports.
        - The content should be approximately 400-500 words.
        - Please ensure accuracy and clarity in your report.
        - Ensure the content is coherent.
        - Use markdown to response

        Respond in the following JSON format:

        ```json
        {{
            "content": "<FULL CONTENT OF THE REPORT GOES HERE>",
            "short_summary": "<A concise summary of the content, less than two lines>"
        }}
        ```
    """
