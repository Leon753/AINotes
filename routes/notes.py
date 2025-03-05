# app/routes/notes.py
import uuid
import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import verify_token
from database import get_db
from models import Note
from services import s3_service, transcription_service


router = APIRouter()

@router.get("/notes/")
async def get_notes(
    db: AsyncSession = Depends(get_db), 
    auth_data: dict = Depends(verify_token)
):
    user_id = auth_data.get("user_id")
    result = await db.execute(select(Note).where(Note.user_id == user_id))
    notes = result.scalars().all()
    return notes

@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int, 
    db: AsyncSession = Depends(get_db), 
    auth_data: dict = Depends(verify_token)
):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != auth_data.get("user_id"):
        raise HTTPException(status_code=403, detail="Unauthorized to delete this note")
    
    file_key = note.file_url.split("/")[-1]
    try:
        s3_service.delete_file_from_s3(file_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deleting file from S3")
    
    await db.delete(note)
    await db.commit()
    return {"message": "Note and associated file deleted successfully"}

@router.post("/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db), 
    auth_data: dict = Depends(verify_token)
):
    try:
        file_ext = file.filename.split(".")[-1].lower()
        allowed_formats = {"flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"}
        if file_ext not in allowed_formats:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        
        file_key = f"{uuid.uuid4()}.{file_ext}"
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="File is empty.")
        
        file_obj_s3 = io.BytesIO(file_bytes)
        file_obj_transcribe = io.BytesIO(file_bytes)
        
        file_url = s3_service.upload_fileobj_to_s3(file_obj_s3, file_key)
        
        content_type = file.content_type or "audio/mpeg"
        
        transcript_text = transcription_service.transcribe_audio_file(
            file_obj_transcribe, f"audio.{file_ext}", content_type
        )
        summary = transcription_service.summarize_transcript(transcript_text)
        
        new_note = Note(
            filename=file.filename, 
            file_url=file_url, 
            transcription=summary, 
            user_id=auth_data.get("user_id")
        )
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)
        
        return {
            "id": new_note.id,
            "file_url": file_url,
            "filename": file.filename,
            "transcription": summary,
            "user_id": auth_data.get("user_id")
        }
    except Exception as e:
        print("General Transcription Endpoint Error:", e)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
