from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import notes 
from auth.auth import router as auth_router
from auth.auth import verify_token

app = FastAPI(title="AI Notes", description="AI-powered note-taking assistant", version="1.0.0")

app.include_router(notes.router, prefix="/api", tags=["notes"],dependencies=[Depends(verify_token)])
app.include_router(auth_router, prefix="/api", tags=["auth"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Notes API is running"}