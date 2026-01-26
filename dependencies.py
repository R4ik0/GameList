from fastapi import HTTPException, Depends



from src.models.user import *
from authentification import *


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    token_data = decode_access_token(token)
    if token_data.username is None:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



def require_roles(*roles):
    async def dep(current_user: UserDB = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return dep