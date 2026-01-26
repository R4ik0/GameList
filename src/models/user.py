from typing import Optional, Dict
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import json
import sqlite3


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
data_path = "data/"


class UserDB(BaseModel):
    id : int
    username: str
    password: str
    gamelist: Dict[int, float] = {}
    role: str


def get_user(id: int) -> Optional[UserDB]:
    conn = sqlite3.connect(data_path +"users.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, username, password, gamelist, role
    FROM user
    WHERE id = ?
    """, (id, ))

    row = cursor.fetchone()
    conn.close()
    if row:
        id, username, password, data_json, role = row
        data = json.loads(data_json)
        return UserDB(
            id = id, 
            username = username,
            password = password, 
            gamelist = {int(k): v for k, v in data.items()}, 
            role = role
        )
    return None


def create_user(username: str, password: str, role: str = "user") -> Optional[UserDB]:
    conn = sqlite3.connect(data_path + "users.db")
    cursor = conn.cursor()


    cursor.execute(
        "SELECT id FROM user WHERE username = ?",
        (username,)
    )
    if cursor.fetchone():
        conn.close()
        print(f"❌ L'utilisateur '{username}' existe déjà")
        return None


    cursor.execute("SELECT MAX(id) FROM user")
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1


    hashed = pwd_context.hash(password)
    user = UserDB(
        id=new_id,
        username=username,
        password=hashed,
        role=role
    )


    cursor.execute("""
    INSERT INTO user (id, username, password, gamelist, role)
    VALUES (?, ?, ?, ?, ?)
    """, (
        user.id,
        user.username,
        user.password,
        json.dumps(user.gamelist),
        user.role
    ))

    conn.commit()
    conn.close()

    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def authenticate_user(id: int, password: str) -> Optional[UserDB]:
    user = get_user(id)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

create_user("admin", "adminpass", role="admin")
create_user("user", "userpass", role="user")