from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from src.models.tokens import Token, RefreshRequest, create_access_token, create_refresh_token, decode_token
from src.models.user import authenticate_user, create_user
from dependencies import get_current_user



router = APIRouter(prefix="", tags=["auth"])



# -----------------------
# LOGIN
# -----------------------
@router.post(
    "/login", 
    response_model=Token,
    responses={
        422: {"description": "Validation error: Username is required or too long"},
        401: {"description": "Invalid username or password"}
    }
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if not form_data.username:
        raise HTTPException(status_code=422, detail="Username is required")
    if len(form_data.username) > 100:
        raise HTTPException(status_code=422, detail="Username too long")
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")


    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    return Token(access_token=access_token, refresh_token=refresh_token)





# -----------------------
# SIGNIN
# -----------------------
@router.post(
    "/signin", 
    response_model=Token,
    responses={
        400: {"description": "Username already exists"},
    }
)
async def signin(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], role = Annotated[str, Form(default="user")]):
    # Créer l'utilisateur
    user = create_user(
        username=form_data.username,
        password=form_data.password,
        role=role
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Créer access + refresh token
    access_token = create_access_token(data={"sub": user['username']})
    refresh_token = create_refresh_token(data={"sub": user['username']})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


# -----------------------
# ROUTE PROTÉGÉE
# -----------------------
@router.get("/protected")
async def protected(current_user: Annotated[dict, Depends(get_current_user)]):
    return {"message": f"Hello {current_user['username']}, this is protected"}


# -----------------------
# REFRESH TOKEN
# -----------------------
@router.post(
    "/refresh", 
    response_model=Token,
    responses={
        401: {"description": "Invalid refresh token or token payload"}
    }
)
async def refresh_token(request: RefreshRequest):
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    access = create_access_token({"sub": username})
    refresh = create_refresh_token({"sub": username})
    return Token(access_token=access, refresh_token=refresh)
