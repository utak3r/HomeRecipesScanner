import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
import dotenv

dotenv.load_dotenv()

auth_scheme = HTTPBearer()

GOOGLE_CLIENT_IDS = [
    os.getenv("GOOGLE_CLIENT_ID_WEB"),
    os.getenv("GOOGLE_CLIENT_ID_ANDROID")
]
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",")

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        id_info = id_token.verify_oauth2_token(
            token.credentials, 
            requests.Request(), 
            audience=GOOGLE_CLIENT_IDS
        )

        email = id_info.get("email")
        
        if email not in ALLOWED_USERS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Użytkownik {email} nie ma uprawnień do tej aplikacji."
            )

        return id_info
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub przedawniony token Google."
        )
