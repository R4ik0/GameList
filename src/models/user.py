from typing import Optional, Dict
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Optional, Dict
from passlib.context import CryptContext
from data.database import supabase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
data_path = "data/"

def get_user(username: str) -> Optional[dict]:
    res = (
        supabase
        .table("users")
        .select("*")
        .eq("username", username)
        .maybe_single()
        .execute()
    )
    return res.data if res else None



def create_user(username: str, password: str, role: str = "user") -> Optional[dict]:
    # Vérifier existence
    existing = (
        supabase
        .table("users")
        .select("id")
        .eq("username", username)
        .execute()
    )

    if existing.data:
        print(f"❌ L'utilisateur '{username}' existe déjà")
        return None

    hashed = pwd_context.hash(password)

    user = {
        "username": username,
        "password": hashed,
        "role": role,
        "gamelist": {}
    }

    res = supabase.table("users").insert(user).execute()
    return res.data[0] if res.data else None


def get_user_gameslist(username: str) -> Optional[Dict]:
    user = get_user(username)
    return user["gamelist"] if user else None


def update_user_gameslist(user: dict) -> None:
    supabase.table("users") \
        .update({"gamelist": user["gamelist"]}) \
        .eq("username", user["username"]) \
        .execute()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user
