import uuid
import jwt
import datetime
import os
from fastapi import APIRouter, HTTPException, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("SECRET_KEY")

security = HTTPBearer() 
router = APIRouter()

# ✅ Middleware function to verify token in requests
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials  # Keep the token for frontend storage
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")  # Extract user_id from JWT payload
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"token": token, "user_id": user_id} 

# API Route for Generating Guest Token
@router.post("/generate-token")
async def generate_token():
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=12)  # Expires in 1 hour
    payload = {"user_id": str(uuid.uuid4()), "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    user_id = payload.get("user_id")  # Extract user_id from JWT payload
    return {"token": token, "user_id": user_id}

