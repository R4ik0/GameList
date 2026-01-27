from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.models.game import get_game_from_igdb, get_X_games, search_game, get_name_from_attribute_id

router = APIRouter(prefix="", tags=["igdb"])


@router.post("/get_game")
async def get_game_from_id(id: int):
    game = get_game_from_igdb(id)
    return game

@router.post("/get_attribute_name")
async def get_attribute_name(attribute: str, id: int):
    name = get_name_from_attribute_id(attribute, id)
    return name

@router.post("/recommendation")
async def get_games(X: int):
    results = get_X_games(X)
    return results

@router.post("/search")
async def get_games_from_name(name: str):
    game_list = search_game(name)
    return game_list