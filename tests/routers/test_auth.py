import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch
from unittest.mock import AsyncMock

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from src.routers.auth_router import router
from src.models.user import UserDB
from dependencies import get_current_user

# Créer une app FastAPI temporaire pour tester le router
app = FastAPI()
app.include_router(router)

client = TestClient(app)


# ----------------------------
# LOGIN
# ----------------------------
@patch("src.routers.auth_router.authenticate_user")
@patch("src.routers.auth_router.create_access_token")
@patch("src.routers.auth_router.create_refresh_token")
def test_login_success(mock_refresh, mock_access, mock_auth):
    mock_auth.return_value = UserDB(
        id=1,
        username="alice",
        password="hashed",
        gamelist={},
        role="user"
    )
    mock_access.return_value = "access123"
    mock_refresh.return_value = "refresh123"

    response = client.post(
        "/login",
        data={"username": "alice", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "access123"
    assert data["refresh_token"] == "refresh123"
    assert data["token_type"] == "bearer"


@patch("src.routers.auth_router.authenticate_user")
def test_login_fail_invalid_credentials(mock_auth):
    mock_auth.return_value = None
    response = client.post(
        "/login",
        data={"username": "bob", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect credentials"


# ----------------------------
# SIGNIN
# ----------------------------
@patch("src.routers.auth_router.create_user")
@patch("src.routers.auth_router.create_access_token")
@patch("src.routers.auth_router.create_refresh_token")
def test_signin_success(mock_refresh, mock_access, mock_create_user):
    mock_create_user.return_value = UserDB(
        id=2,
        username="charlie",
        password="hashed",
        gamelist={},
        role="user"
    )
    mock_access.return_value = "access123"
    mock_refresh.return_value = "refresh123"

    response = client.post(
        "/signin",
        data={"username": "charlie", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "access123"
    assert data["refresh_token"] == "refresh123"


@patch("src.routers.auth_router.create_user")
def test_signin_fail_existing_user(mock_create_user):
    mock_create_user.return_value = None
    response = client.post(
        "/signin",
        data={"username": "existing", "password": "pass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


# ----------------------------
# PROTECTED ROUTE
# ----------------------------
def test_protected_route():
    async def override_get_current_user():
        return UserDB(
            id=1,
            username="alice",
            password="hashed",
            gamelist={},
            role="user"
        )

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = client.get("/protected")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello alice, this is protected"

    app.dependency_overrides.clear()


# ----------------------------
# REFRESH TOKEN
# ----------------------------
@patch("src.routers.auth_router.decode_token")
@patch("src.routers.auth_router.create_access_token")
@patch("src.routers.auth_router.create_refresh_token")
def test_refresh_token_success(mock_refresh, mock_access, mock_decode):
    mock_decode.return_value = {"sub": "alice", "type": "refresh"}
    mock_access.return_value = "new_access"
    mock_refresh.return_value = "new_refresh"

    response = client.post(
        "/refresh", 
        json={"refresh_token": "token123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "new_access"
    assert data["refresh_token"] == "new_refresh"


@patch("src.routers.auth_router.decode_token")
def test_refresh_token_fail_invalid(mock_decode):
    mock_decode.return_value = {}
    response = client.post(
        "/refresh",
        json={"refresh_token": "badtoken"}  # ⚠️ utilise data pour Form
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


@patch("src.routers.auth_router.decode_token")
def test_refresh_token_fail_no_sub(mock_decode):
    mock_decode.return_value = {"type": "refresh"}
    response = client.post(
        "/refresh",
        json={"refresh_token": "token123"}  # ⚠️ utilise data pour Form
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token payload"
