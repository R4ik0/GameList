from pickle import GET
from fastapi import APIRouter, Depends


from src.models.user import UserDB, update_user_gameslist
from dependencies import get_current_user



router = APIRouter(prefix="", tags=["user"])


# -----------------------
# GET CURRENT USER
# -----------------------
@router.get("/me", response_model=UserDB)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    print(current_user)
    return current_user

# curl -X GET "http://localhost:8000/me" \
#   -H "Authorization: Bearer "


# -----------------------
# GET USER GAMESLIST
# -----------------------
@router.get("/GamesList", response_model=dict)
async def get_gameslist(current_user: UserDB = Depends(get_current_user)):
    return current_user.gamelist


# -----------------------
# ADD OR UPDATE A GAME IN USER'S GAMESLIST
# -----------------------
@router.post("/GamesList/{game_id}/{rating}", response_model=dict)
async def add_or_update_game(
    game_id: int,
    rating: float,
    current_user: UserDB = Depends(get_current_user)
):
    current_user.gamelist[game_id] = rating
    update_user_gameslist(current_user)
    return current_user.gamelist