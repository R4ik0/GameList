from unittest.mock import patch
from fastapi.testclient import TestClient

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from main import app
from src.models.game import Game

client = TestClient(app)

# -----------------------
# /get_game
# -----------------------
@patch("src.routers.igdb_router.get_game_from_igdb")
def test_get_game(mock_get_game):
    mock_get_game.return_value = Game(
        id=1,
        name="Zelda",
        genres=[1],
        themes=[2],
        game_modes=[3],
        platforms=[4],
        storyline="Story",
        cover="cover_url"
    )

    response = client.post("/get_game?id=1")

    assert response.status_code == 200
    assert response.json()["name"] == "Zelda"


# -----------------------
# /get_attribute_name
# -----------------------
@patch("src.routers.igdb_router.get_name_from_attribute_id")
def test_get_attribute_name(mock_get_name):
    mock_get_name.return_value = "RPG"

    response = client.post("/get_attribute_name?attribute=genres&id=12")

    assert response.status_code == 200
    assert response.json() == "RPG"


# -----------------------
# /recommendation
# -----------------------
@patch("src.routers.igdb_router.get_X_games")
def test_recommendation(mock_get_x):
    mock_get_x.return_value = [
        {"id": 1, "name": "Game 1"},
        {"id": 2, "name": "Game 2"},
        {"id": 3, "name": "Game 3"},
    ]

    response = client.post("/recommendation?X=3")

    assert response.status_code == 200
    assert len(response.json()) == 3


# -----------------------
# /search
# -----------------------
@patch("src.routers.igdb_router.search_game")
def test_search_game(mock_search):
    mock_search.return_value = [
        {"id": 1, "name": "Zelda"},
        {"id": 2, "name": "Zelda BOTW"}
    ]

    response = client.post("/search?name=zelda")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Zelda"


# -----------------------
# /full_game
# -----------------------
@patch("src.routers.igdb_router.get_cover_url")
@patch("src.routers.igdb_router.get_name_from_attribute_id")
@patch("src.routers.igdb_router.get_game_from_igdb")
def test_full_game(
    mock_get_game,
    mock_get_name,
    mock_get_cover
):
    mock_get_game.return_value = Game(
        id=1,
        name="Zelda",
        genres=[1, 2],
        themes=[3],
        game_modes=[4],
        platforms=[5],
        storyline="Epic adventure",
        cover=None
    )

    mock_get_name.side_effect = lambda attr, id: f"{attr}_{id}"
    mock_get_cover.return_value = "cover_url"

    response = client.post("/full_game?id=1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Zelda"
    assert data["genres"] == ["genres_1", "genres_2"]
    assert data["themes"] == ["themes_3"]
    assert data["game_modes"] == ["game_modes_4"]
    assert data["platforms"] == ["platforms_5"]
    assert data["cover"] == "cover_url"
