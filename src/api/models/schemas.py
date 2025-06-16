from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class AgentsRequest(BaseModel):
    agents: List[str]
    provider: str
    model: str

class TitleRequest(BaseModel):
    title: str

class AppendRequest(BaseModel):
    title: str
    message: Message

class FolderCreateRequest(BaseModel):
    filepath: str

class FolderContent(BaseModel):
    foldername: str
    contents: List[str]

class FolderListResponse(BaseModel):
    files: List[FolderContent]