from typing import List
from pydantic import BaseModel


class AgentsRequest(BaseModel):
    agents: List[str]  # List of strings
    model: str
    provider:str

class FolderRequest(BaseModel):
    db :str


class Message(BaseModel):
    role: str
    content: str

class FolderContent(BaseModel):
    foldername: str
    contents: List[str]

class FolderListResponse(BaseModel):
    files: List[FolderContent]

class FolderCreateRequest(BaseModel):
    filepath: str