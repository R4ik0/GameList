from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.models.token_model import Token
from src.models.user import UserDB, authenticate_user
from authentification import create_access_token, create_refresh_token, decode_token
from dependencies import get_current_user



router = APIRouter(prefix="", tags=["auth"])



# -----------------------
# LOGIN
# -----------------------
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Vérifie l'utilisateur dans la base
    user: UserDB = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    # Crée access + refresh token
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token)
#curl -X POST "http://localhost:8000/login"   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=admin"   -d "password=adminpass"
#

# -----------------------
# ROUTE PROTÉGÉE
# -----------------------
@router.get("/protected")
async def protected(current_user: UserDB = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, this is protected"}

# -----------------------
# REFRESH TOKEN
# -----------------------
@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    access = create_access_token({"sub": username})
    refresh = create_refresh_token({"sub": username})
    return Token(access_token=access, refresh_token=refresh)
