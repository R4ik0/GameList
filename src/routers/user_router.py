from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from src.models.token_model import Token
from src.models.user import UserDB, authenticate_user, create_user
from authentification import create_access_token, create_refresh_token, decode_token
from dependencies import get_current_user



router = APIRouter(prefix="", tags=["user"])


# -----------------------
# GET CURRENT USER
# -----------------------
@router.get("/me", response_model=UserDB)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    return current_user


# -----------------------
# GET USER GAMESLIST
# -----------------------
@router.get("/GamesList", response_model=dict)
async def get_gameslist(current_user: UserDB = Depends(get_current_user)):
    return current_user.gamelist