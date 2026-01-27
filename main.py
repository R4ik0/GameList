from fastapi import FastAPI, Depends
from src.routers import auth_router, igdb_router, user_router
from dependencies import get_current_user
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GameList API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",      # live-server
        "http://127.0.0.1:5500",
        "https://r4ik0.github.io",    # GitHub Pages
        "https://r4ik0.github.io/GameList",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(igdb_router.router)
app.include_router(user_router.router)

@app.get("/")
async def root():
    return {"message": "API ready. Use /docs for interactive docs."}

