from fastapi import FastAPI, Depends
from routers import auth_router, igdb_router
from dependencies import get_current_user
import uvicorn

app = FastAPI(title="GameList API", version="1.0.0")


app.include_router(auth_router.router)
app.include_router(igdb_router.router)


@app.get("/")
async def root():
    return {"message": "API ready. Use /docs for interactive docs."}

