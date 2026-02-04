from pydantic import BaseModel
from dotenv import load_dotenv
import random as rd
import requests
import os
from typing import List, Optional
from data.database import supabase



load_dotenv()
CLIENT_ID = os.environ["CLIENT_ID"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]



# Do we add those ? 
# language_supports: list, developers: not sure how to access, player_perspectives: list, keywords: list
class Game(BaseModel):
    id: int
    name: str
    genres: Optional[List[int|str]] = None
    themes: Optional[List[int|str]] = None
    game_modes: Optional[List[int|str]] = None
    platforms: Optional[List[int|str]] = None
    storyline: Optional[str] = None
    cover: Optional[str] = None



def get_game_from_igdb(game_id):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields *; where id = {game_id};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    response = response.json()[0]
    game = Game(
        id = game_id,
        name=response.get("name"),
        genres=response.get("genres",[]),
        themes=response.get("themes",[]),
        game_modes=response.get("game_modes",[]),
        platforms=response.get("platforms",[]),
        storyline=response.get("storyline"),
        cover = None
    )
    return game



def get_game_from_bdd(game_id) -> Optional[dict]:
    res = (
        supabase
        .table("games")
        .select("*")
        .eq("id", game_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None



def get_name_from_attribute_id(attribute, attribute_id_list):
    url = f"https://api.igdb.com/v4/{attribute}/"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    if not attribute_id_list:
        return []
    id_string = ", ".join(str(i) for i in attribute_id_list)
    body = f"fields name; where id = ({id_string});"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    name = response.json()
    return name



def get_best_X_games(X):
    url = "https://api.igdb.com/v4/games/"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields id; limit {X}; sort rating desc; where game_type=(0,1,4,8,9) & rating_count > 500;"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    response = response.json()
    return response


def get_cover_url(game_id):
    url = "https://api.igdb.com/v4/covers"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields image_id; where game = {game_id};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    if len(response.json()) == 0:
        return "co86z1"
    response = response.json()[0]
    return response.get("image_id")



def search_game(name):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields id, name, game_type; search \"{name}\"; where game_type=(0,1,4,8,9);"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()
    for i in range(len(response.json())):
        image = get_cover_url(response.json()[i]['id'])
        result[i]['image'] = image
    return result



def get_similar_games(id_list):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    if len(id_list) == 0:
        return []
    id_string = ", ".join(str(i) for i in id_list)
    body = f"fields similar_games; where id = ({id_string});"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()
    return result



def get_best_similar_games(id_list):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    if len(id_list) == 0:
        return []
    id_string = ", ".join(str(i) for i in id_list)
    body = f"fields id; where id = ({id_string}) & rating_count > 50; sort rating desc; limit {len(id_list)};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()
    return result





def create_game_in_bdd(game_id: str) -> Optional[dict]:
    # Vérifier existence
    existing = (
        supabase
        .table("games")
        .select("*")
        .eq("id_game", game_id)
        .execute()
    )

    if existing.data:
        print(f"Le jeu '{game_id}' existe déjà")
        return None

    game = get_game_from_igdb(game_id)
    genres, themes, game_modes, platforms = [], [], [], []
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
    
    cover = get_cover_url(game_id)

    json_game = {
        "id_game": game.id,
        "name": game.name,
        "genres": genres,
        "themes": themes,
        "game_modes": game_modes,
        "platforms": platforms,
        "storyline": game.storyline,
        "cover": cover
    }

    res = supabase.table("games").insert(json_game).execute()
    return res.data[0] if res.data else None
