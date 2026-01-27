import pytest
from unittest.mock import patch, Mock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from src.models.game import Game, get_game_from_igdb, get_X_games

# ----------------------------
# Test Game model
# ----------------------------
def test_game_model_creation():
    game = Game(
        id=1,
        name="Test Game",
        genres=["Action"],
        themes=["Fantasy"],
        game_modes=["Singleplayer"],
        platforms=["PC"],
        storyline="Test storyline"
    )
    assert game.id == 1
    assert game.name == "Test Game"
    assert "Action" in game.genres
    assert "Fantasy" in game.themes
    assert game.storyline == "Test storyline"

# ----------------------------
# Test get_game_from_igdb
# ----------------------------
@patch("src.models.game.requests.post")
def test_get_game_from_igdb_returns_game(mock_post):
    # Mock de la réponse JSON de l'API
    mock_response = Mock()
    mock_response.json.return_value = [{
        "name": "Mock Game",
        "genres": ["Action", "Adventure"],
        "themes": ["Fantasy"],
        "game_modes": ["Singleplayer"],
        "platforms": ["PC"],
        "storyline": "Mock storyline"
    }]
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    game = get_game_from_igdb(1234)
    assert isinstance(game, Game)
    assert game.id == 1234
    assert game.name == "Mock Game"
    assert "Action" in game.genres

@patch("src.models.game.requests.post")
def test_get_game_from_igdb_raises_for_status(mock_post):
    # Simuler une exception HTTP
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("API error")
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        get_game_from_igdb(1234)

# ----------------------------
# Test get_X_games
# ----------------------------
@patch("src.models.game.requests.post")
def test_get_X_games_returns_list(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = [{"id": 1, "name": "Game1"}, {"id": 2, "name": "Game2"}]
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    games = get_X_games(2)
    assert isinstance(games, list)
    assert len(games) == 2
    assert games[0]["name"] == "Game1"

@patch("src.models.game.requests.post")
def test_get_X_games_raises_for_status(mock_post):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = Exception("API error")
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        get_X_games(5)
