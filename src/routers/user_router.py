from pickle import GET
from fastapi import APIRouter, Depends
from typing import Annotated


from src.models.user import update_user_gameslist, search_users
from src.models.game import create_game_in_bdd
from dependencies import get_current_user



router = APIRouter(prefix="", tags=["user"])


# -----------------------
# GET CURRENT USER
# -----------------------
@router.get("/me", response_model=dict)
async def read_users_me(current_user = Annotated[dict, Depends(get_current_user)]):
    print(current_user)
    return current_user

# curl -X GET "http://localhost:8000/me" \
#   -H "Authorization: Bearer "



# -----------------------
# GET USER GAMESLIST
# -----------------------
@router.get("/GamesList", response_model=dict)
async def get_gameslist(current_user = Annotated[dict, Depends(get_current_user)]):
    return current_user["gamelist"]



# -----------------------
# ADD OR UPDATE A GAME IN USER'S GAMESLIST
# -----------------------
@router.post("/GamesList/{game_id}/{rating}", response_model=dict)
async def add_or_update_game(
    game_id: int,
    rating: float,
    current_user = Annotated[dict, Depends(get_current_user)]
):
    current_user["gamelist"][game_id] = rating
    update_user_gameslist(current_user)
    create_game_in_bdd(game_id)
    return current_user["gamelist"]



# -----------------------
# DELETE A GAME IN USER'S GAMESLIST
# -----------------------
@router.delete("/GamesList/{game_id}", response_model=dict)
async def delete_game( 
    game_id: int,
    current_user = Annotated[dict, Depends(get_current_user)]
):
    if game_id in current_user["gamelist"]:
        del current_user["gamelist"][game_id]
        update_user_gameslist(current_user)
    return current_user["gamelist"]



@router.post("/searchUser")
async def search_user(query:str):
    return search_users(query)