import boto3
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from database import get_db
from models import Note
from sqlalchemy.future import select


load_dotenv()

router = APIRouter()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

ALLOWED_EXTENSIONS = {"mp3", "wav"}

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only MP3 and WAV files are allowed")

    # Generate a unique filename
    unique_filename = f"{uuid4()}.{file_extension}"

    # Upload file to S3
    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET_NAME, unique_filename)
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"

        note = Note(filename=unique_filename, file_url=file_url)
        db.add(note)
        await db.commit()
        await db.refresh(note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    return {"file_url": file_url, "filename": unique_filename}

@router.get("/upload/", response_model=list[dict])
async def list_files(db: AsyncSession = Depends(get_db)):
    """Retrieve all files from the database"""
    result = await db.execute(select(Note))
    files = result.scalars().all()

    return [
        {"id": file.id, "filename": file.filename, "file_url": file.file_url}
        for file in files
    ]

@router.get("/upload/{file_id}")
async def get_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific file's metadata"""
    file = await db.get(Note, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    return {"id": file.id, "filename": file.filename, "file_url": file.file_url}

@router.get("/upload/{file_id}/download")
async def download_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """Generate a presigned URL for secure file download"""
    file = await db.get(Note, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": file.filename},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return {"presigned_url": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating download URL: {str(e)}")
