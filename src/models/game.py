from pydantic import BaseModel
from dotenv import load_dotenv
import random as rd
import requests
import os
from typing import List, Optional


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
        genres=response.get("genres"),
        themes=response.get("themes"),
        game_modes=response.get("game_modes"),
        platforms=response.get("platforms"),
        storyline=response.get("storyline"),
        cover = None
    )
    return game


def get_name_from_attribute_id(attribute, attribute_id):
    url = f"https://api.igdb.com/v4/{attribute}/"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields name; where id = {attribute_id};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    name = response.json()[0]
    return name.get("name")


def get_X_games(X):
    url = "https://api.igdb.com/v4/games/"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields id; limit {X}; offset {rd.randint(0,10000)};"
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
    response = response.json()[0]
    return response.get("image_id")


def search_game(name):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields id, name, game_type; search \"{name}\"; where game_type=(0,8,9);"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()
    for i in range(len(response.json())):
        image = get_cover_url(response.json()[i]['id'])
        result[i]['image'] = image
    return result


def get_similar_games(id):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields similar_games; where id = {id};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()[0]
    return result.get("similar_games",[])


def get_rating(id):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields rating; where id = {id};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()[0]
    return result.get('rating', 0)