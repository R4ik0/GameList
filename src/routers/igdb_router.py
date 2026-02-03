from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.models.game import Game, get_game_from_igdb, get_best_X_games, search_game, get_name_from_attribute_id, get_cover_url, get_similar_games, get_rating
from src.models.recommendation import GameRecommender
from dependencies import get_current_user
from operator import itemgetter



router = APIRouter(prefix="", tags=["igdb"])
recommender = GameRecommender()
recommender.load_from_supabase()



@router.post("/get_game")
async def get_game_from_id(id: int):
    game = get_game_from_igdb(id)
    return game



@router.post("/get_attribute_name")
async def get_attribute_name(attribute: str, id: int):
    name = get_name_from_attribute_id(attribute, id)
    return name



@router.post("/recommendation")
async def get_recommended_games(top_k: int = 10, current_user = Depends(get_current_user)):
    try:
        if len(current_user["gamelist"]) == 0:
            best_X_games = get_best_X_games(top_k)
            return [x.get("id") for x in best_X_games]
        all_similar_games = []
        for game_id in current_user["gamelist"]:
            similar_games = get_similar_games(game_id)
            for game in similar_games:
                couple = (game,get_rating(game))
                if game not in current_user["gamelist"] and couple not in all_similar_games:
                    all_similar_games.append(couple)
        all_similar_games.sort(key=itemgetter(1), reverse=True)
        results = recommender.recommend_from_candidates(current_user["id"], [x[0] for x in all_similar_games[:100]], top_k)
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
    game = get_game_from_igdb(id)
    genres,themes,game_modes,platforms = [], [], [], []
    for i in game.genres:
        genres.append(get_name_from_attribute_id('genres', i))
    for i in game.themes:
        themes.append(get_name_from_attribute_id('themes', i))
    for i in game.game_modes:
        game_modes.append(get_name_from_attribute_id('game_modes', i))
    for i in game.platforms:
        platforms.append(get_name_from_attribute_id('platforms', i))
    cover = get_cover_url(id)
    return Game(id = game.id, name = game.name, genres = genres, themes = themes, game_modes = game_modes, platforms = platforms, storyline = game.storyline, cover = cover)



@router.post("/get_essential")
async def get_essential(id: int):
    game_name = get_name_from_attribute_id("games",id)
    cover = get_cover_url(id)
    return {"id": id, "name": game_name, "cover": cover}
