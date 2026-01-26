from pydantic import BaseModel
import requests
from a_ignorer import CLIENT_ID, ACCESS_TOKEN



# Do we add those ? 
# language_supports: list, developers: not sure how to access, player_perspectives: list, keywords: list, cover: int idk how to print it on the front
class Game(BaseModel):
    id: int
    name: str
    genres: list
    themes: list
    game_modes: list
    platforms: list
    storyline: str



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

    response = response.json()

    game = Game(id = game_id,
                name = response.name,
                genres = response.genres,
                themes = response.themes,
                game_modes = response.game_modes,
                platforms = response.platforms,
                storyline = response.storyline
                )
    return game