from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.models.game import Game, get_game_from_igdb, get_best_X_games, search_game, get_name_from_attribute_id, get_cover_url, get_similar_games, get_best_similar_games
from game_recommender import GameRecommender
from dependencies import get_current_user
from operator import itemgetter
from data.database import supabase
from typing import List



router = APIRouter(prefix="", tags=["igdb"])



@router.post("/get_game")
async def get_game_from_id(id: int):
    game = get_game_from_igdb(id)
    return game



@router.post("/recommendation")
async def get_recommended_games(top_k: int = 10, current_user = Depends(get_current_user)):
    try:
        if len(current_user["gamelist"]) == 0:
            best_X_games = get_best_X_games(top_k)
            return [x.get("id") for x in best_X_games]
        recommender = GameRecommender()
        recommender.load_from_supabase()
        temp = get_similar_games(current_user["gamelist"])
        similar_games = []
        for i in temp:
            similar_games += i.get("similar_games",[])
        list_temp = [i.get("id") for i in get_best_similar_games(similar_games) if f"{i.get('id')}" not in current_user["gamelist"].keys()][:100]
        results = recommender.recommend_from_candidates(current_user["id"], list_temp, top_k)
        return [x[0] for x in results]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="User not supported by recommendation model"
        )



@router.post("/search")
async def get_games_from_name(name: str):
    game_list = search_game(name)
    return game_list



@router.post("/full_game")
async def get_full_game(id: int):
    genres, themes, game_modes, platforms = [], [], [], []
    existing = (
        supabase
        .table("games")
        .select("*")
        .eq("id_game", id)
        .execute()
    )
    if existing.data:
        return Game(
            id = existing.data[0]["id_game"],
            name = existing.data[0]["name"],
            genres = existing.data[0]["genres"],
            themes = existing.data[0]["themes"],
            game_modes = existing.data[0]["game_modes"],
            platforms = existing.data[0]["platforms"],
            storyline = existing.data[0]["storyline"],
            cover = existing.data[0]["cover"]
        )
    game = get_game_from_igdb(id)
    mapping = [
        ("genres", game.genres, genres),
        ("themes", game.themes, themes),
        ("game_modes", game.game_modes, game_modes),
        ("platforms", game.platforms, platforms),
    ]
    for attr, values, target in mapping:
        target.extend(
            item["name"]
            for item in get_name_from_attribute_id(attr, values)
        )
    cover = get_cover_url([id])[0]
    return Game(id = game.id, name = game.name, genres = genres, themes = themes, game_modes = game_modes, platforms = platforms, storyline = game.storyline, cover = cover)



@router.post("/get_essential")
async def get_essential(ids: List[int]):
    existing = (
        supabase
        .table("games")
        .select("id_game, name, cover")
        .in_("id_game", ids)
        .execute()
    )

    data = existing.data or []
    dict_by_id = {}
    for game in data:
        game["id"] = game.pop("id_game")
        dict_by_id[game["id"]] = game

    if len(existing.data) == len(ids):
        return existing.data
    else:
        missing_ids = set(ids) - {item["id"] for item in existing.data}
        print(f"Missing IDs: {missing_ids}")
        images = get_cover_url(list(missing_ids))
        games = get_name_from_attribute_id("games", list(missing_ids))
        for i in range(len(missing_ids)):
            dict_by_id[games[i]["id"]] = {
                "id": games[i]["id"],
                "name": games[i]["name"],
                "cover": images[i]
            }
        
        return [dict_by_id[i] for i in ids]
