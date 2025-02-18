from database import Base  # Import from centralized location
from sqlalchemy import Column, Integer, String, Text

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    file_url = Column(String, nullable=False)
    transcription = Column(Text, nullable=True)
