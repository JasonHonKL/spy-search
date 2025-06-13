import datetime


def quick_search_prompt(query, data):
    return f"""
    Today is {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.

    # Task Overview

    You have been presented with the following question:
    > {query}

    # Reference Material

    Below is a list of the most recent and relevant information available:
    {data}

    # Instructions

    1. Evaluate the relevance of the provided data to the question. Disregard irrelevant data.
    2. Integrate useful data thoughtfully into your response.
    3. Include APA-style inline citations **formatted as clickable Markdown links**. For example, cite as:
        - Correct: (Example, 20xx) [Example](https://example.com)
        - Incorrect: [(Example, 20xx) (Example)][https://example.com]
    4. Write your response in clear, professional language with appropriate Markdown formatting:
        - Use `#` for main titles
        - Use `##` for subtitles
    5. Include only relevant content.
    6. Ensure inline citations appear **inside parentheses**, followed by the Markdown link wrapped around the source title (as shown in the example).
    7. Include the table if you think it is necessary.

    Please ensure the response is informative, concise, and easy to read.
    """
