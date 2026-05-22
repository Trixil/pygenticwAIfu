from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .core.lifespan import lifespan
from .core.paths import CHARACTER_IMAGES_DIR, LOADOUT_IMAGES_DIR, STATIC_DIR
from .routes import characters, chats, health, loadouts, pages

agenticwAIfuApp = FastAPI(lifespan=lifespan)

agenticwAIfuApp.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")

agenticwAIfuApp.mount(
    "/character-images",
    StaticFiles(directory=CHARACTER_IMAGES_DIR),
    name="character-images"
)
agenticwAIfuApp.mount(
    "/loadout-images",
    StaticFiles(directory=LOADOUT_IMAGES_DIR),
    name="loadout-images"
)

agenticwAIfuApp.include_router(health.router)
agenticwAIfuApp.include_router(pages.router)
agenticwAIfuApp.include_router(characters.router)
agenticwAIfuApp.include_router(loadouts.router)
agenticwAIfuApp.include_router(chats.router)
