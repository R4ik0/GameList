from pydantic import BaseModel
from dotenv import load_dotenv
import random as rd
import requests
import os
from typing import List, Optional

from pprint import pprint


load_dotenv()
CLIENT_ID = os.environ["CLIENT_ID"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]


# Do we add those ? 
# language_supports: list, developers: not sure how to access, player_perspectives: list, keywords: list, cover: int idk how to print it on the front
class Game(BaseModel):
    id: int
    name: str
    genres: Optional[List[int]] = None
    themes: Optional[List[int]] = None
    game_modes: Optional[List[int]] = None
    platforms: Optional[List[int]] = None
    storyline: Optional[str] = None



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
        storyline=response.get("storyline")
    )
    return game

pprint(get_game_from_igdb(2003).model_dump())


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
    response = response.json()
    return response