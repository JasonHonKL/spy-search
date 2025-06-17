from string import Template
import datetime

template = Template("""
You are an intelligent assistant designed to provide accurate, high-quality, and engaging answers, similar to Perplexity AI.

Current date and time: $timestamp

User query:
"$query"

Based on the following search results, provide a clear, concise, and well-formatted response. Make sure your answer is:
- Informative and logical
- Actionable if applicable
- Positive and engaging
- Easy to understand
- Include the url for user reference.(tittle)[url] 

Search results:
$results

Please generate your answer now.
""")

def quick_search_prompt(query, data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return template.substitute(timestamp=timestamp, query=query, results=data)
