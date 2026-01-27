from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.models.game import get_game_from_igdb, get_X_games, search_game

router = APIRouter(prefix="", tags=["igdb"])


@router.post("/get_game")
async def get_game_from_id(id: int):
    game = get_game_from_igdb(id)
    return game

@router.post("/recommendation")
async def get_games(X: int):
    results = get_X_games(X)
    return results

@router.post("/search")
async def get_games_from_name(name: str):
    game_list = search_game(name)
    return game_list