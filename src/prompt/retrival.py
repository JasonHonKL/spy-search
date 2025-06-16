def retrieval_prompt(content: str, filepath: str) -> str:
    return f"""
You are provided with the following text content extracted from a file:

\"\"\"
{content}
\"\"\"

The source file path is:
{filepath}

Please analyze the content and generate a structured JSON response containing the following fields:

- "title": A concise and descriptive title capturing the main topic of the content.
- "summary": A detailed summary of approximately 200 words that captures all key points and insights.
- "brief_summary": A very short summary (1-2 sentences) highlighting the core idea.
- "keywords": A list of relevant keywords or key phrases that best represent the content.
- "url": The original file path.

Return the result strictly in the following JSON format:

{{
  "title": "string",
  "summary": "string",
  "brief_summary": "string",
  "keywords": ["string", "string", ...],
  "url": "{filepath}"
}}

Ensure the JSON is properly formatted and valid.
"""
