from fastapi import FastAPI
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.arenas.router import router as arenas_router
from app.modules.games.router import router as games_router
from app.modules.leaderboards.router import router as leaderboards_router
from app.modules.slots.router import router as slots_router
from app.modules.sessions.router import router as sessions_router
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.modules.pages.router import router as pages_router
from app.modules.streaming.router import router as streaming_router

app = FastAPI(
    title="WRC Platform",
    debug=settings.DEBUG,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(auth_router)
app.include_router(arenas_router)
app.include_router(games_router)
app.include_router(leaderboards_router)
app.include_router(slots_router)
app.include_router(sessions_router)
app.include_router(pages_router)
app.include_router(streaming_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}