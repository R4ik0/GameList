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
        genres=response.get("genres",[]),
        themes=response.get("themes",[]),
        game_modes=response.get("game_modes",[]),
        platforms=response.get("platforms",[]),
        storyline=response.get("storyline"),
        cover = None
    )
    return game



def get_name_from_attribute_id(attribute, attribute_id_list):
    url = f"https://api.igdb.com/v4/{attribute}/"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    if len(attribute_id_list) == 0:
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
    body = f"fields id; limit {X}; sort rating desc;"
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



def get_rating(id_list):
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    if len(id_list) == 0:
        return []
    id_string = ", ".join(str(i) for i in id_list)
    body = f"fields rating; where id = ({id_string});"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    result = response.json()
    return result