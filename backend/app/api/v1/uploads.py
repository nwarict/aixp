from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.storage_service import StorageService

router = APIRouter(prefix="/uploads", tags=["File Upload"])
storage_service = StorageService()

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    file_url = await storage_service.upload_file(
        file_data=contents,
        filename=file.filename,
        content_type=file.content_type
    )
    return {
        "filename": file.filename,
        "url": file_url,
        "size": len(contents),
        "content_type": file.content_type
    }
