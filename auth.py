import jwt
import datetime
import os
from fastapi import APIRouter, HTTPException, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("SECRET_KEY")

security = HTTPBearer() 
router = APIRouter()

# ✅ Function to generate a guest token
def generate_guest_token():
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=12)  # Expires in 1 hour
    payload = {"exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# ✅ Middleware function to verify token in requests
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return token  # Token is valid, proceed

# API Route for Generating Guest Token
@router.post("/generate-token")
async def generate_token():
    return {"token": generate_guest_token()}

