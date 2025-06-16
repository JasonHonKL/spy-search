import os
from typing import List
from fastapi import HTTPException, UploadFile
from ..models.schemas import FolderContent

class FileService:
    def __init__(self):
        self.base_path = "./local_files"
        self._ensure_base_directory()
    
    def _ensure_base_directory(self) -> None:
        """Ensure base directory exists"""
        os.makedirs(self.base_path, exist_ok=True)
    
    def get_folder_list(self) -> List[FolderContent]:
        """Get list of folders and their contents"""
        folders = []
        
        try:
            for item in os.listdir(self.base_path):
                full_path = os.path.join(self.base_path, item)
                if os.path.isdir(full_path):
                    contents = os.listdir(full_path)
                    folders.append(FolderContent(foldername=item, contents=contents))
            return folders
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def create_folder(self, folder_path: str) -> bool:
        """Create a new folder"""
        try:
            full_path = os.path.join(self.base_path, folder_path)
            os.makedirs(full_path, exist_ok=True)
            return True
        except Exception:
            return False
    
    def select_folder(self, folder_name: str) -> str:
        """Select and validate folder"""
        folder_path = os.path.join(self.base_path, folder_name)
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Folder not found")
        
        if not os.path.isdir(folder_path):
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        return folder_path
    
    async def upload_file(self, file: UploadFile, filepath: str) -> bool:
        """Upload file to specified path"""
        try:
            full_path = os.path.join(self.base_path, filepath)
            dir_path = os.path.dirname(full_path)
            
            if not os.path.exists(dir_path):
                raise HTTPException(status_code=404, detail="Directory not found")
            
            with open(full_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return True
        except Exception:
            return False
    
    def delete_file(self, filepath: str) -> bool:
        """Delete specified file"""
        try:
            full_path = os.path.join(self.base_path, filepath)
            
            if not os.path.exists(full_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.isfile(full_path):
                raise HTTPException(status_code=400, detail="Path is not a file")
            
            os.remove(full_path)
            return True
        except Exception:
            return False
    
    def get_file_path(self, filepath: str) -> str:
        """Get full file path and validate"""
        full_path = os.path.join(self.base_path, filepath)
        
        if not os.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        return full_path