import pytest
import sqlite3
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "")))

from src.models.user import *

# --------------------------
# Fixtures
# --------------------------

@pytest.fixture
def clean_db():
    """
    Vide la table user avant chaque test
    """
    conn = sqlite3.connect(data_path + "users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user")
    conn.commit()
    conn.close()
    yield
    # Nettoyage après test (optionnel)
    conn = sqlite3.connect(data_path + "users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user")
    conn.commit()
    conn.close()

# --------------------------
# Tests
# --------------------------

def test_create_and_get_user(clean_db):
    # 1️⃣ Création utilisateur
    username = "alice"
    password = "password123"
    role = "admin"

    user = create_user(username=username, password=password, role=role)
    assert user is not None
    assert user.username == username
    assert user.role == role
    assert pwd_context.verify(password, user.password)  # Vérifie le hash

    # 2️⃣ Récupération par ID
    retrieved = get_user(user.id)
    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.username == user.username
    assert retrieved.role == user.role
    assert isinstance(retrieved.gamelist, dict)

def test_create_duplicate_user(clean_db):
    username = "bob"
    password = "secret"

    # 1️⃣ Créer le premier utilisateur
    user1 = create_user(username=username, password=password)
    assert user1 is not None

    # 2️⃣ Tenter de créer un doublon
    user2 = create_user(username=username, password=password)
    assert user2 is None  # doit retourner None pour doublon


# --------------------------
# Tests verify_password
# --------------------------

def test_verify_password():
    plain = "mysecret"
    hashed = pwd_context.hash(plain)

    assert verify_password(plain, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

# --------------------------
# Tests authenticate_user
# --------------------------

def test_authenticate_user(clean_db):
    username = "charlie"
    password = "supersecret"
    wrong_password = "nopass"

    # Créer un utilisateur
    user = create_user(username=username, password=password)
    assert user is not None

    # Authentification correcte
    auth_user = authenticate_user(user.id, password)
    assert auth_user is not None
    assert auth_user.username == username

    # Mauvais mot de passe
    auth_wrong = authenticate_user(user.id, wrong_password)
    assert auth_wrong is None

    # Utilisateur inexistant
    auth_none = authenticate_user("unknown", password)
    assert auth_none is None