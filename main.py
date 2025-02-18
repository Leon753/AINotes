from fastapi import Depends, FastAPI
from routes import notes, upload
from auth import generate_guest_token, verify_token


app = FastAPI(title="AI Notes", description="AI-powered note-taking assistant", version="1.0.0")

app.include_router(notes.router, prefix="/api", tags=["notes"],dependencies=[Depends(verify_token)])
app.include_router(upload.router, prefix="/files", tags=["uploads"],dependencies=[Depends(verify_token)])

@app.get("/get-token/")
def get_guest_token():
    token = generate_guest_token()
    return {"token": token}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Notes API is running"}