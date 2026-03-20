from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer()

class LoginRequest(BaseModel):
    id_token: str

@router.post("/login")
async def login(data: LoginRequest):
    try:
        # Verify Google Token
        id_info = id_token.verify_oauth2_token(
            data.id_token, 
            requests.Request(), 
            audience=[settings.GOOGLE_CLIENT_ID_WEB, settings.GOOGLE_CLIENT_ID_ANDROID]
        )

        email = id_info.get("email")
        allowed_users = settings.ALLOWED_USERS.split(",")
        
        if email not in allowed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Użytkownik {email} nie ma uprawnień do tej aplikacji."
            )

        # Create Backend Token
        access_token = create_access_token(
            subject=email,
            extra_claims={
                "name": id_info.get("name"),
                "picture": id_info.get("picture")
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "email": email,
                "name": id_info.get("name"),
                "picture": id_info.get("picture")
            }
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub przedawniony token Google."
        )

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    # 1. Try to verify as Backend JWT
    try:
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        if email:
            return {"email": email}
    except JWTError:
        pass

    # 2. Try to verify as Google ID Token (backward compatibility / Swagger)
    try:
        id_info = id_token.verify_oauth2_token(
            token.credentials, 
            requests.Request(), 
            audience=[settings.GOOGLE_CLIENT_ID_WEB, settings.GOOGLE_CLIENT_ID_ANDROID]
        )
        email = id_info.get("email")
        allowed_users = settings.ALLOWED_USERS.split(",")
        
        if email not in allowed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Użytkownik {email} nie ma uprawnień do tej aplikacji."
            )
        return id_info
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub przedawniony token."
        )
