from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/notes", tags=["CRM - Notes"])

@router.get("", response_model=list[NoteResponse])
async def list_notes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    related_type: str = None,
    related_id: str = None,
    skip: int = 0,
    limit: int = 100
):
    query = select(Note).where(
        Note.tenant_id == current_user.tenant_id,
        Note.is_deleted == False
    )
    if related_type:
        query = query.where(Note.related_type == related_type)
    if related_id:
        query = query.where(Note.related_id == related_id)

    query = query.order_by(desc(Note.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=NoteResponse)
async def create_note(
    data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = Note(
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        **data.model_dump()
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.tenant_id == current_user.tenant_id
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.tenant_id == current_user.tenant_id
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)

    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.tenant_id == current_user.tenant_id
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.is_deleted = True
    from datetime import datetime, timezone
    note.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "Note deleted"}
