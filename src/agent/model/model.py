from typing import Optional


class Data_row:
    """
    Two types of Data_row ,
    a file response
    """

    filepath: Optional[str | None]
    title: str
    brief_summary: str
    keywords: list[str]
    url: str


class Response(object):
    next_router: str
    query: str
    data: list[str | Data_row]
