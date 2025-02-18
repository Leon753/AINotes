from dotenv import load_dotenv
from fastapi import FastAPI
from routes import notes, upload


app = FastAPI(title="AI Notes", description="AI-powered note-taking assistant", version="1.0.0")

app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(upload.router, prefix="/files", tags=["uploads"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Notes API is running"}