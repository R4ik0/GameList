import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi import HTTPException
from jose import jwt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", "")))

from src.models.tokens import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_token,
    TokenData,
)
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE


# ----------------------------
# Tests pour create_access_token
# ----------------------------
def test_create_access_token_contains_username_and_exp():
    data = {"sub": "alice"}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "alice"
    assert "exp" in payload

def test_create_access_token_custom_expiration():
    data = {"sub": "bob"}
    token = create_access_token(data, expiration_delta=timedelta(minutes=10))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_time = datetime.utcfromtimestamp(payload["exp"])
    assert (exp_time - datetime.utcnow()) <= timedelta(minutes=10, seconds=1)  # small margin


# ----------------------------
# Tests pour create_refresh_token
# ----------------------------
def test_create_refresh_token_contains_type_and_exp():
    data = {"sub": "charlie"}
    token = create_refresh_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "charlie"
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_create_refresh_token_custom_expiration():
    data = {"sub": "dave"}
    token = create_refresh_token(data, expires_delta=timedelta(minutes=5))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_time = datetime.utcfromtimestamp(payload["exp"])
    assert (exp_time - datetime.utcnow()) <= timedelta(minutes=5, seconds=1)


# ----------------------------
# Tests pour decode_access_token
# ----------------------------
def test_decode_access_token_returns_token_data():
    data = {"sub": "eve"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert isinstance(decoded, TokenData)
    assert decoded.username == "eve"

def test_decode_access_token_raises_on_invalid_token():
    with pytest.raises(HTTPException):
        decode_access_token("invalidtoken")

def test_decode_access_token_raises_if_no_sub():
    token = jwt.encode({"exp": datetime.utcnow() + timedelta(minutes=5)}, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException):
        decode_access_token(token)

def test_decode_access_token_raises_on_expired_token():
    data = {"sub": "frank"}
    # On force l'expiration dans le passé
    with patch("src.models.tokens.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = datetime(2000, 1, 1)
        token = create_access_token(data, expiration_delta=timedelta(minutes=1))
    with pytest.raises(HTTPException):
        decode_access_token(token)


# ----------------------------
# Tests pour decode_token
# ----------------------------
def test_decode_token_returns_dict_for_valid_token():
    data = {"sub": "george"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert isinstance(decoded, dict)
    assert decoded["sub"] == "george"

def test_decode_token_returns_empty_dict_for_invalid_token():
    result = decode_token("badtoken")
    assert result == {}
