import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Note
from dotenv import load_dotenv
import boto3
import asyncio
import os

load_dotenv()
# ✅ Setup S3 client
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
s3_client = boto3.client("s3")

async def cleanup_old_notes(db: AsyncSession):
    """Deletes expired notes and their associated files from S3."""
    expiration_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=1)  # Change as needed

    result = await db.execute(select(Note).where(Note.created_at < expiration_threshold))
    old_notes = result.scalars().all()

    for note in old_notes:
        try:
            file_key = note.file_url.split("/")[-1]  # Extract file key
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=file_key)  # Delete from S3
            print(f"✅ Deleted {file_key} from S3")

            await db.delete(note)  # Delete from DB
        except Exception as e:
            print(f"❌ Error deleting {file_key}: {e}")

    await db.commit()
    print("✅ Cleanup completed!")