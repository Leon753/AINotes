from database import Base  # Import from centralized location
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    file_url = Column(String, nullable=False)
    transcription = Column(Text, nullable=True)
    user_id = Column(String, index=True) 
    created_at = Column(DateTime, server_default=func.now())
