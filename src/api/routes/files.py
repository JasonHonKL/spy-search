from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional, List
import os
from ..models.schemas import FolderCreateRequest, FolderListResponse
from ..services.file_service import FileService

router = APIRouter()
file_service = FileService()

@router.get("/folder_list", response_model=FolderListResponse)
async def get_folder():
    """Get list of folders - SAME ENDPOINT"""
    folders = file_service.get_folder_list()
    return FolderListResponse(files=folders)

@router.post("/create_folder")
async def create_folder(filepath: FolderCreateRequest):
    """Create new folder - SAME ENDPOINT"""
    success = file_service.create_folder(filepath.filepath)
    return {"success": success}

@router.get("/select_folder")
async def select_folder(folder_name: str):
    """Select folder - SAME ENDPOINT"""
    try:
        folder_path = file_service.select_folder(folder_name)
        return {"success": True, "selected_folder": folder_name}
    except HTTPException as e:
        raise e

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...), filepath: str = Form(...)):
    """Upload file - SAME ENDPOINT"""
    success = await file_service.upload_file(file, filepath)
    
    if success:
        return {"success": True, "filename": file.filename, "filepath": filepath}
    else:
        return {"success": False, "error": "Upload failed"}

@router.post("/delete_file")
async def delete_file(filepath: str):
    """Delete file - SAME ENDPOINT"""
    success = file_service.delete_file(filepath)
    
    if success:
        return {"success": True, "deleted_file": filepath}
    else:
        return {"success": False, "error": "Delete failed"}

@router.get("/download_file/{filepath:path}")
async def download_file(filepath: str):
    """Download file - SAME ENDPOINT"""
    try:
        full_path = file_service.get_file_path(filepath)
        filename = os.path.basename(filepath)
        
        return FileResponse(
            path=full_path,
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException as e:
        raise e