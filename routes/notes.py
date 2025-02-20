import uuid
import boto3
import os
import io
import openai
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth import verify_token
from models import Note
from database import get_db
from pydantic import BaseModel

router = APIRouter()

# AWS S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Request body schema
class NoteCreate(BaseModel):
    filename: str
    transcription: str

@router.post("/notes/")
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    new_note = Note(filename=note.filename, transcription=note.transcription)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

@router.get("/notes/")
async def get_notes(
    db: AsyncSession = Depends(get_db), 
    auth_data: dict = Depends(verify_token)
):
    user_id = auth_data.get("user_id")  # Extract user_id
    result = await db.execute(select(Note).where(Note.user_id == user_id))
    notes = result.scalars().all()

    return notes

@router.get("/notes/{note_id}")
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/notes/{note_id}")
async def update_note(note_id: int, note_data: NoteCreate, db: AsyncSession = Depends(get_db)):
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.filename = note_data.filename
    note.transcription = note_data.transcription
    await db.commit()
    await db.refresh(note)
    return note

@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    """Deletes a note and removes the associated audio file from S3."""
    note = await db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Extract file name from URL
    file_url = note.file_url
    if file_url:
        file_key = file_url.split("/")[-1]  # Extracts 'filename.mp3' from the full S3 URL
        print("FILE URL", file_key)
        print("FILE URL", S3_BUCKET_NAME)

        try:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=file_key)
            print(f"✅ Deleted file {file_key} from S3")
        except Exception as e:
            print(f"❌ Failed to delete from S3: {e}")
            raise HTTPException(status_code=500, detail="Error deleting file from S3")

    # Delete from database
    await db.delete(note)
    await db.commit()
    return {"message": "Note and associated file deleted successfully"}

@router.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), auth_data: str = Depends(verify_token)):
    try:
        file_ext = file.filename.split(".")[-1].lower()

        allowed_formats = {"flac", "m4a", "mp3", "mp4", "mpeg", "mpga", "oga", "ogg", "wav", "webm"}
        if file_ext not in allowed_formats:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload an MP3, WAV, or other supported format.")

        file_key = f"{uuid.uuid4()}.{file_ext}"
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Error: File is empty after reading.")

        file_obj = io.BytesIO(file_bytes)

        s3_client.upload_fileobj(file_obj, S3_BUCKET_NAME, file_key)
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"

        file_obj = io.BytesIO(file_bytes)

        content_type = file.content_type or "audio/mpeg"  # Default to MP3 MIME type if unknown

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio." + file_ext, file_obj, content_type)  # Ensure correct file format
        )

        if not transcript.text:
            raise HTTPException(status_code=500, detail="Transcription returned empty text.")
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Summarize this transcript into bullet points."},
                {"role": "user", "content": transcript.text}
            ]
        )
        summary = response.choices[0].message.content

        new_note = Note(filename=file.filename, file_url=file_url, transcription=summary, user_id=auth_data.get("user_id"))
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)

        return {
            "file_url": file_url,
            "filename": file.filename,
            "transcription": summary,
            "user_id": auth_data.get("user_id")
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")