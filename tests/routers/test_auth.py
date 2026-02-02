from fastapi.testclient import TestClient
from types import SimpleNamespace
from unittest.mock import patch

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from main import app
from dependencies import get_current_user

client = TestClient(app)




# ============================
# Tests
# ============================


@patch("src.routers.auth_router.authenticate_user")
@patch("src.routers.auth_router.create_access_token")
@patch("src.routers.auth_router.create_refresh_token")
def test_login_mocked(
    mock_refresh,
    mock_access,
    mock_auth
):
    mock_auth.return_value = {"username": "mockuser"}
    mock_access.return_value = "access123"
    mock_refresh.return_value = "refresh123"

    response = client.post(
        "/login",
        data={
            "username": "mockuser",
            "password": "mockpass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "access123"
    assert response.json()["refresh_token"] == "refresh123"


@patch("src.routers.auth_router.authenticate_user")
def test_login_invalid_credentials(mock_auth):
    mock_auth.return_value = None

    response = client.post(
        "/login",
        data={
            "username": "baduser",
            "password": "badpass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 401



@patch("src.routers.auth_router.create_user")
@patch("src.routers.auth_router.create_access_token")
@patch("src.routers.auth_router.create_refresh_token")
def test_signin_mocked_success(
    mock_refresh,
    mock_access,
    mock_create_user
):
    # --- Mocks ---
    mock_create_user.return_value = SimpleNamespace(
        username="mockuser",
        role="user"
    )
    mock_access.return_value = "access_mock"
    mock_refresh.return_value = "refresh_mock"

    response = client.post(
        "/signin",
        data={
            "username": "mockuser",
            "password": "mockpass",
            "role": "user"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    body = response.json()

    assert body["access_token"] == "access_mock"
    assert body["refresh_token"] == "refresh_mock"

    mock_create_user.assert_called_once_with(
        username="mockuser",
        password="mockpass",
        role="user"
    )


@patch("src.routers.auth_router.create_user")
def test_signin_mocked_duplicate_username(mock_create_user):
    mock_create_user.return_value = None

    response = client.post(
        "/signin",
        data={
            "username": "existing_user",
            "password": "whatever"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"



def test_protected_mocked():
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "mockuser"
    }

    response = client.get("/protected")

    assert response.status_code == 200
    assert "mockuser" in response.json()["message"]

    app.dependency_overrides.clear()



@patch("src.routers.auth_router.decode_token")
@patch("src.routers.auth_router.create_access_token")
@patch("src.routers.auth_router.create_refresh_token")
def test_refresh_mocked(
    mock_refresh,
    mock_access,
    mock_decode
):
    mock_decode.return_value = {
        "sub": "mockuser",
        "type": "refresh"
    }
    mock_access.return_value = "new_access"
    mock_refresh.return_value = "new_refresh"

    response = client.post(
        "/refresh",
        json={"refresh_token": "fake_refresh"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "new_access"
