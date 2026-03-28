from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import game
from .game_manager import game_manager

app = FastAPI(title="Fight For Pearl API", version="1.0.0")

# CORS 允许 Vue 开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router)

@app.get("/")
def root():
    return {"message": "Fight For Pearl API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}