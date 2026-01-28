from fastapi.testclient import TestClient
from unittest.mock import MagicMock

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from main import app
from dependencies import get_current_user

client = TestClient(app)


# -----------------------
# MOCK USER
# -----------------------
def mock_user():
    return {
        "id": 1,
        "username": "alice",
        "password": "hashed",
        "gamelist": {1: 4.5, 2: 3.0},
        "role": "user"
    }


# -----------------------
# DEPENDENCY OVERRIDE
# -----------------------
async def override_get_current_user():
    return mock_user()


# -----------------------
# SETUP / TEARDOWN
# -----------------------
def setup_module():
    app.dependency_overrides[get_current_user] = override_get_current_user


def teardown_module():
    app.dependency_overrides.clear()


# -----------------------
# /me
# -----------------------
def test_get_me():
    response = client.get("/me")

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


# -----------------------
# /GamesList (GET)
# -----------------------
def test_get_gameslist():
    response = client.get("/GamesList")

    assert response.status_code == 200
    assert response.json() == {"1": 4.5, "2": 3.0}


# -----------------------
# ADD GAME
# -----------------------
def test_add_or_update_game(monkeypatch):
    monkeypatch.setattr(
        "src.routers.user_router.update_user_gameslist",
        MagicMock()
    )

    response = client.post("/GamesList/3/4.0")

    assert response.status_code == 200
    assert response.json()["3"] == 4.0


# -----------------------
# UPDATE EXISTING GAME
# -----------------------
def test_update_existing_game(monkeypatch):
    monkeypatch.setattr(
        "src.routers.user_router.update_user_gameslist",
        MagicMock()
    )

    response = client.post("/GamesList/1/5.0")

    assert response.status_code == 200
    assert response.json()["1"] == 5.0


# -----------------------
# DELETE GAME
# -----------------------
def test_delete_game(monkeypatch):
    monkeypatch.setattr(
        "src.routers.user_router.update_user_gameslist",
        MagicMock()
    )

    response = client.delete("/GamesList/1")

    assert response.status_code == 200
    assert "1" not in response.json()


# -----------------------
# DELETE NON-EXISTING GAME
# -----------------------
def test_delete_non_existing_game(monkeypatch):
    mock_update = MagicMock()
    monkeypatch.setattr(
        "src.routers.user_router.update_user_gameslist",
        mock_update
    )

    response = client.delete("/GamesList/999")

    assert response.status_code == 200
    assert response.json() == {"1": 4.5, "2": 3.0}
    mock_update.assert_not_called()
