from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import notes, upload
from auth import generate_guest_token, verify_token


app = FastAPI(title="AI Notes", description="AI-powered note-taking assistant", version="1.0.0")

app.include_router(notes.router, prefix="/api", tags=["notes"],dependencies=[Depends(verify_token)])
app.include_router(upload.router, prefix="/files", tags=["upload"],dependencies=[Depends(verify_token)])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust if needed)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-token/")
def get_guest_token():
    token = generate_guest_token()
    return {"token": token}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Notes API is running"}