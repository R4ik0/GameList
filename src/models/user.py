from typing import Optional, Dict
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserDB(BaseModel):
    username: str
    password: str
    role: str

class User(BaseModel):
    username: str
    role: str



_users_db: Dict[str, UserDB] = {}

def get_user(username: str) -> Optional[UserDB]:
    return _users_db.get(username)


def create_user(username: str, password: str, role = 'user'):
    hashed = pwd_context.hash(password)
    user = UserDB(username=username, password=hashed, role=role)
    _users_db[username] = user
    return user