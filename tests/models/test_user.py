import pytest

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from data.database import supabase
from src.models.user import (
    create_user,
    get_user,
    authenticate_user,
    verify_password,
    get_user_gameslist,
    update_user_gameslist
)


# ============================
# Constantes de test
# ============================

TEST_USERS = [
    {
        "username": "pytest_user_1",
        "password": "pytestUpass",
        "role": "user"
    },
    {
        "username": "pytest_admin_1",
        "password": "pytestApass",
        "role": "admin"
    }
]


# ============================
# Fixture de setup / teardown
# ============================

@pytest.fixture(scope="module")
def test_users():
    """
    Crée les users de test avant les tests
    et les supprime après.
    """
    created_users = []

    # --- SETUP ---
    for u in TEST_USERS:
        user = create_user(
            username=u["username"],
            password=u["password"],
            role=u["role"]
        )
        assert user is not None
        created_users.append(u)

    yield created_users

    # --- TEARDOWN ---
    for u in created_users:
        supabase.table("users") \
            .delete() \
            .eq("username", u["username"]) \
            .execute()


# ============================
# Tests
# ============================

TEST_USERS[0]['password']


def test_get_user(test_users):
    user = get_user(TEST_USERS[0]['username'])
    assert user is not None
    assert user["username"] == TEST_USERS[0]['username']
    assert user["role"] == TEST_USERS[0]['role']


def test_authenticate_user_success(test_users):
    user = authenticate_user(TEST_USERS[0]['username'], TEST_USERS[0]['password'])
    assert user is not None
    assert user["username"] == TEST_USERS[0]['username']


def test_authenticate_user_wrong_password(test_users):
    user = authenticate_user(TEST_USERS[0]['username'], "wrongpassword")
    assert user is None


def test_authenticate_user_not_found(test_users):
    user = authenticate_user("does_not_exist", "password")
    assert user is None


def test_password_is_hashed(test_users):
    user = get_user(TEST_USERS[0]['username'])
    assert user["password"] != TEST_USERS[0]['password']
    assert verify_password(TEST_USERS[0]['password'], user["password"])


def test_admin_role(test_users):
    admin = get_user(TEST_USERS[1]['username'])
    assert admin is not None
    assert admin["role"] == TEST_USERS[1]['role']


def test_get_user_gameslist_empty(test_users):
    gamelist = get_user_gameslist(TEST_USERS[0]['username'])
    assert isinstance(gamelist, dict)
    assert gamelist == {}


def test_update_user_gameslist(test_users):
    user = get_user(TEST_USERS[0]['username'])
    user["gamelist"] = {
        '250616': 10
    }

    update_user_gameslist(user)

    updated = get_user_gameslist(TEST_USERS[0]['username'])
    assert '250616' in updated
    assert updated['250616'] == 10