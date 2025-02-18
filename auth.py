import jwt
import datetime
import os
from fastapi import HTTPException, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


SECRET_KEY = os.getenv("SECRET_KEY")
TOKEN_EXPIRATION_HOURS = 24
security = HTTPBearer() 

# ✅ Function to generate a guest token
def generate_guest_token():
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
    token = jwt.encode({"exp": expiration}, SECRET_KEY, algorithm="HS256")
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
