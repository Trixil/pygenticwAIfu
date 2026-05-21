from fastapi import FastAPI, Form, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi import Request
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import os
import time
import glob
import json
from pathlib import Path
import shutil

try:
    from . import definitions, file_io, htmlHelpers
except ImportError:
    import definitions
    import file_io
    import htmlHelpers

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
CHARACTERS_DIR = APP_DIR / "characters"
LOADOUTS_DIR = APP_DIR / "loadouts"
CHATS_DIR = APP_DIR / "chats"
CHARACTER_IMAGES_DIR = CHARACTERS_DIR / "images"
LOADOUT_IMAGES_DIR = LOADOUTS_DIR / "images"

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Get your tissues out...")
    time.sleep(0.25)
    print("""
            ⣇⣿⠘⣿⣿⣿⡿⡿⣟⣟⢟⢟⢝⠵⡝⣿⡿⢂⣼⣿⣷⣌⠩⡫⡻⣝⠹⢿⣿⣷
            ⡆⣿⣆⠱⣝⡵⣝⢅⠙⣿⢕⢕⢕⢕⢝⣥⢒⠅⣿⣿⣿⡿⣳⣌⠪⡪⣡⢑⢝⣇
            ⡆⣿⣿⣦⠹⣳⣳⣕⢅⠈⢗⢕⢕⢕⢕⢕⢈⢆⠟⠋⠉⠁⠉⠉⠁⠈⠼⢐⢕⢽
            ⡗⢰⣶⣶⣦⣝⢝⢕⢕⠅⡆⢕⢕⢕⢕⢕⣴⠏⣠⡶⠛⡉⡉⡛⢶⣦⡀⠐⣕⢕
            ⡝⡄⢻⢟⣿⣿⣷⣕⣕⣅⣿⣔⣕⣵⣵⣿⣿⢠⣿⢠⣮⡈⣌⠨⠅⠹⣷⡀⢱⢕
            ⡝⡵⠟⠈⢀⣀⣀⡀⠉⢿⣿⣿⣿⣿⣿⣿⣿⣼⣿⢈⡋⠴⢿⡟⣡⡇⣿⡇⡀⢕
            ⡝⠁⣠⣾⠟⡉⡉⡉⠻⣦⣻⣿⣿⣿⣿⣿⣿⣿⣿⣧⠸⣿⣦⣥⣿⡇⡿⣰⢗⢄
            ⠁⢰⣿⡏⣴⣌⠈⣌⠡⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣬⣉⣉⣁⣄⢖⢕⢕⢕
            ⡀⢻⣿⡇⢙⠁⠴⢿⡟⣡⡆⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣵⣵⣿
            ⡻⣄⣻⣿⣌⠘⢿⣷⣥⣿⠇⣿⣿⣿⣿⣿⣿⠛⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
            ⣷⢄⠻⣿⣟⠿⠦⠍⠉⣡⣾⣿⣿⣿⣿⣿⣿⢸⣿⣦⠙⣿⣿⣿⣿⣿⣿⣿⣿⠟
            ⡕⡑⣑⣈⣻⢗⢟⢞⢝⣻⣿⣿⣿⣿⣿⣿⣿⠸⣿⠿⠃⣿⣿⣿⣿⣿⣿⡿⠁⣠
            ⡝⡵⡈⢟⢕⢕⢕⢕⣵⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣿⣿⣿⣿⣿⠿⠋⣀⣈⠙
            ⡝⡵⡕⡀⠑⠳⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⢉⡠⡲⡫⡪⡪⡣ 
          """)
    
    time.sleep(1)

    if not os.path.isdir("characters"):
        os.mkdir("characters")
    
    if not os.path.isdir("chats"):
        os.mkdir("chats")
    
    if not os.path.isdir("loadouts"):
        os.mkdir("loadouts")
    
    yield
    print("Time to clean up crodie")
    time.sleep(0.25)
    print("""
          ⠀  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡟⢰⠀⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⠠⠀⠀⡇⣯⡄⢀⢀⢰⠢⡀⢣⠘⡄⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⢂⠑⡀⡇⢿⠐⡈⠪⠄⣧⣐⣄⠿⡱⢄⠀⢺⠤⢀⢰⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⣀⠀⠑⢦⡤⢤⣥⡬⢧⠼⢧⠬⠯⡙⣷⣖⠧⡙⣒⣧⠵⣀⠩⣢⢿⣌⢓⢄⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⢄⠳⡌⠙⠡⣍⡓⠦⣌⠭⢬⣤⣡⠐⢎⢼⠷⢞⣼⣬⣱⣽⣲⢫⢻⢕⣍⠣⡱⡽⡲⡠⣀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⡀⢕⡢⢈⠣⡾⢌⡃⠠⢘⣧⣋⠙⠦⡭⢭⡝⠶⣳⠷⢮⣽⣶⣷⣭⣹⢷⡷⣿⣯⣷⡨⢶⣿⣵⢌⡦⡀⠀⠀
            ⠀⠀⠀⠀⠀⢀⢈⠢⣹⣢⣨⠖⢍⡒⠶⠨⣡⣒⣷⣶⣭⡗⣚⠚⡭⠝⠴⠦⣤⠍⣛⣓⢯⣬⣿⣽⣽⡿⣿⣿⣮⣾⡽⢷⣲⢱⡀⢀
            ⠀⠀⠀⠀⠀⠈⢋⢼⢽⢯⢦⡙⣓⠞⡛⣳⣙⣾⣭⣧⣄⣀⠤⠐⠒⠉⠊⠙⢛⣿⣟⣯⣾⣭⣻⣮⣻⣿⣿⣿⣿⣿⣦⠘⣞⡌⡿⣼
            ⠀⠀⠀⠀⠀⠀⠀⣱⢻⡔⢤⣉⣐⣤⣋⣥⡤⣽⡷⠒⠌⡀⢀⣠⡤⠚⢈⣉⡴⠯⠛⠻⢃⢛⣻⣿⣷⣿⣿⡿⣿⣿⣿⣧⣿⣶⣲⢻
            ⠀⠀⠀⠀⠀⠀⠀⠀⠑⠺⢅⣝⣛⣥⣍⡁⢀⣉⣠⣴⠞⣋⣽⠡⢴⠾⣋⡡⢄⣲⣈⠭⠙⠛⣻⣿⣿⣷⣿⣿⣽⣿⣿⣿⣿⣿⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠒⡤⢤⢶⠚⣋⡩⢤⣖⣍⣉⣾⢋⣬⣛⣷⡿⠋⣨⣕⣦⠓⠁⠀⣀⠴⢎⣉⠵⢛⣻⣩⣽⣿⣿⣿⣿⣿⣿⣋⣟
            ⠀⠀⠀⠀⠀⠀⠀⠀⣴⣙⡽⣯⡝⣋⣡⣴⣤⢿⢡⣿⣿⡿⢊⣤⠾⠋⡩⠂⢀⣴⡫⠕⣊⠕⢁⠔⢁⡼⠋⠁⡁⣸⣿⣿⣿⣿⣛⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⡇⠀⠀⠀⢠⡀⢸⡻⡴⣷⣩⡟⠩⡠⢊⡠⣰⠟⢁⠄⠊⢀⡴⠋⠔⠉⠀⡘⢰⢀⣿⣿⣿⣿⣿⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⢠⡄⠀⠀⡘⢩⠗⢪⢋⡟⣐⠥⠶⣹⠼⠑⢈⣀⣴⠜⢁⠀⠀⢠⡕⣽⠀⣟⣾⣿⢻⢻⣿⣿⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠚⡁⠋⠀⠠⡦⠢⠴⢥⣎⣜⣡⣶⣾⣶⣾⣿⣭⣽⣠⠴⢃⣔⣪⡞⣱⣷⠸⣼⣟⣧⣟⣼⣟⣿⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⣷⡀⠀⠀⠀⣧⢠⡔⢋⣡⣾⣿⣿⢻⡏⠛⢻⣿⡟⢁⣴⣫⢻⣿⣲⣿⣾⡀⣷⣛⡟⣬⣿⢹⣿⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⣛⠻⢿⣦⠀⠀⠈⠈⢡⡜⣿⡿⠟⡿⠃⠀⣄⢳⣿⡿⣿⢿⡿⣿⣽⣿⣿⡿⣧⣿⣿⣷⣿⠛⢸⣿⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣡⠻⡷⣦⡿⠆⠀⠀⢠⣦⠀⢸⡅⠰⠃⠘⣦⡾⣧⡏⡄⢣⡄⣀⣿⣛⣬⡅⣶⣿⣿⣿⣿⢹⡄⣻⣿⣯⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⢧⠀⣳⡀⠀⢠⣾⡿⠆⢈⣣⠀⠀⠀⡞⠃⠻⢀⠀⢾⣧⣉⣛⣉⣤⣶⣿⡟⠸⡌⢾⠀⣣⣿⡏⢫⡿
            ⠀⠀⠀⠀⠀⠀⠀⣾⣀⠀⠀⠙⠃⠘⠃⠠⣼⡇⠀⠀⢨⡖⠀⠀⠀⠁⠀⠀⠈⠁⠈⠻⢿⣿⣿⣿⠟⡹⠶⠁⡓⡘⣆⠿⠡⢠⡏⡿
            ⠀⠀⠀⠀⠀⠀⠀⠈⠺⢗⣦⣄⣀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠤⠀⠀⠀⠀⣫⣿⣿⣿⠀⢧⢸⠀⡿⢰⢣⢸⡇⡜⣸⣼
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢮⣿⡟⡿⣿⡿⣿⡿⣿⠿⢻⡿⠟⢉⠀⠔⠁⠀⠀⠀⢿⣹⡟⣿⡄⣽⣿⢃⢣⢸⣮⢿⢼⢡⣿⣿
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣧⣵⣾⣾⣿⠿⢻⠇⢀⠔⠁⠀⡜⠐⠀⠄⢐⣿⣎⣿⡹⢷⡄⣿⣿⣼⢿⡟⢹⢀⣡⡽⣽
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⣠⡾⢁⣴⣏⡠⠊⠀⡠⠊⠀⠀⣄⣀⣼⣇⠫⢢⡧⢘⣧⡽⣬⢷⡞⡷⡠⢳⢾⠣⡼
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠖⠁⠀⢀⠟⡹⠋⠁⣴⠁⠀⠀⠀⣸⡟⠀⢦⣁⣬⢡⠷⣫⢵⡘⠸⠇⡷⠯⡍⠸⡔⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⡄⠀⠀⣼⣚⣁⣀⣞⣉⣀⣀⣴⣯⣾⣧⣴⣾⣿⣿⠊⠀⠈⠃⠹⠃⠀⠣⠀⠀⠀⢷⠤
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀
            ⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀
          """)
    time.sleep(1)

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

@agenticwAIfuApp.get("/check-status")
def checkStatus():
    return {"ok": True, "status": "online", "service": "chat"}

@agenticwAIfuApp.get("/static")
def mainpage():
    landing_html = (STATIC_DIR / "landing.html").read_text(encoding="utf-8")
    character_cards_html = renderCharacterCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{CHARACTER_CARDS}}", character_cards_html)
    loadout_cards_html = renderLoadoutCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{LOADOUT_CARDS}}", loadout_cards_html)
    return HTMLResponse(content=landing_html)

@agenticwAIfuApp.get("/chat")
def chatpage():
    return FileResponse(STATIC_DIR / "chatpage.html")

@agenticwAIfuApp.get("/api/ping")
def pong():
    return {"ok": True, "message": "pong"}

@agenticwAIfuApp.post("/api/create-character")
def createCharacter(
    characterName: str = Form(...),
    characterImage: UploadFile = File(...),
    nickname: str = Form(...),
    description: str = Form(...),
    scenario: str = Form(...)
):

    print("bruh")
    if not file_io.validateFilename(characterName):
        return {"validFilename": False}
    
    print("bruh")
    characterFile = CHARACTERS_DIR / "definitions" / (characterName + ".json")
    print("bruh")
    print("bruh")
    imageFileDest = APP_DIR / "characters" / "images" / characterImage.filename

    with imageFileDest.open("wb") as buffer:
        shutil.copyfileobj(characterImage.file, buffer)
    
    newCharacter = definitions.character(
        charName=characterName,
        charNickname=nickname,
        charDesc=description,
        charScenario=scenario,
        charFile=str(Path("characters") / "definitions" / f"{characterName}.json"),
        charImageFile=str(Path("characters") / "definitions" / characterImage.filename)
    )

    file_io.saveChar(newCharacter, characterFile)
    print("bruh")
    return {"validFilename": True}

@agenticwAIfuApp.post("/add-character-card", response_class=HTMLResponse)
def addCharacter(characterName: str = Form(...),
                 characterImage: UploadFile = File(...)) -> HTMLResponse:
    
    charHtml = f"""
        <div class="character-card">
            <img src="/character-images/{characterImage.filename}" alt="Character Image" class="character-image"/>
              <button class="character-edit-button" aria-label="Edit character">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4l10.5-10.5-4-4L4 16v4zM15.5 4.5l4 4 1.2-1.2a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.2 1.2z" />
                </svg>
            </button>
            <div class="character-name">{characterName}</div>
        </div>
        """;

    return HTMLResponse(content=charHtml)

@agenticwAIfuApp.post("/select-character-for-chat")
async def renderChatCardOfCharacter(request: Request):

    data = await request.json()
    characterName = data["characterId"]
    characterCard = file_io.loadChar(str(CHARACTERS_DIR / "definitions" / (characterName + ".json")))
    characterImageName = str(Path(characterCard.charImageFile).name)

    cardHtml = f"""
        <div class="selected-chat-card" data-chat-card-id={characterName}>
            <img src="/character-images/{characterImageName}"
                class="selected-chat-card-image">
            <span class="selected-chat-text">{characterName}</span>
        </div>
    """

    return {"cardHtml": cardHtml}

@agenticwAIfuApp.post("/select-loadout-for-chat")
async def renderChatCardOfLoadout(request: Request):

    data = await request.json()
    loadoutName = data["loadoutId"]
    loadoutCard = file_io.loadLoadout(str(LOADOUTS_DIR / (loadoutName + ".json")))
    loadoutImageName = str(Path(loadoutCard.loadoutImageFile).name)

    cardHtml = f"""
        <div class="selected-chat-card" data-loadout-card-id="{loadoutName}">
            <img src="/loadout-images/{loadoutImageName}"
                class="selected-chat-card-image">
            <span class="selected-chat-text">{loadoutName}</span>
        </div>
    """

    return {"cardHtml": cardHtml}

@agenticwAIfuApp.post("/start-new-chat")
async def startNewChat(request: Request):
    data = await request.json()
    characterIds = data["characterIds"]
    loadoutId = normalize(data["loadoutId"])

    chatFiles = glob.glob(
        str(CHATS_DIR / "*.json")
    )

    chatID = len(chatFiles) + 1

    chatDict = {
        "chatName": "",
        "chatID": chatID,
        "chatFile": f"chats/{chatID}.json",
        "chatAgentLoadout": loadoutId,
        "chatCharacters": characterIds,
        "messages": []
    }

    print("chatDict is", chatDict)
    file_io.saveChat(chatDict, str(CHATS_DIR / f"{chatID}.json"))
    return {"chatID": chatID}

@agenticwAIfuApp.post("/api/save-message")
async def saveMessage(chatMessageInput: str = Form(...), 
                    chatId: str = Form(...),
                    role: str = Form(...)):
    
    chatFile = str(CHATS_DIR / f"{chatId}.json")
    chatCard = file_io.loadChat(chatFile)
    chatMessages = chatCard.messages

    # /#/# USER NAME NOT IMPLEMENTED YET
    newMessage = definitions.message.model_validate({
        "role": role,
        "sender": "Himothy NOT IMPLEMENTED YET",
        "content": chatMessageInput
    })

    chatMessages = chatMessages.append(newMessage)
    chatCard.messages = chatMessages
    
    file_io.saveChat(chatCard.model_dump(), chatFile)

@agenticwAIfuApp.get("/render-new-message", response_class=HTMLResponse)
def renderNewMessage(messageContent: str = Form(...),
                    role: str = Form(...)):
    messageHTML = htmlHelpers.buildMessageHTML(role, messageContent)
    return HTMLResponse(content=messageHTML)

@agenticwAIfuApp.get("/chat/{chatID}", response_class=HTMLResponse)
async def serveNewChat(chatID: str):

    chatCard = file_io.loadChat(str(CHATS_DIR / f"{chatID}.json"))
    chatMessages = chatCard.messages
    messageHTML = """<div class="chat-bubbles">"""
    for message in chatMessages:
        messageHTML += htmlHelpers.buildMessageHTML(message.role, message.content)

    messageHTML += """
        </div>
    """

    convoHeadImgHTML = """<div class="convo-head-imgs">"""
    for characterID in chatCard.chatCharacters:
        characterImageFiles = glob.glob(
            str(CHARACTERS_DIR / "images" / f"{characterID}.*")
        )

        if not characterImageFiles:
            raise FileNotFoundError(f"No image found for {characterID}")
        
        imageFile = Path(characterImageFiles[0]).name
        convoHeadImgHTML += f"""
            <img class="convo-head-img" src="/character-images/{imageFile}">
            """

    convoHeadImgHTML += """
    </div>"""

    pipelineBubbleHTML = f"""
    <div class="pipeline-current">
        <span class="pipeline-label">Current loadout</span>
        <span class="pipeline-name">{chatCard.chatAgentLoadout}</span>
    </div>

    <div class="pipeline-actions">
        <button class="pipeline-action-button">Edit</button>
        <button class="pipeline-action-button">Change</button>
    </div>
    """

    chatPage = (APP_DIR / "templates" / "chat.html").read_text(encoding="utf-8")
    chatPage = chatPage.replace("{{CONVO_HEAD_CHARACTERS}}", convoHeadImgHTML)
    chatPage = chatPage.replace("{{PIPELINE_BUBBLE}}", pipelineBubbleHTML)
    chatPage = chatPage.replace("{{CONVO_MESSAGES}}", messageHTML)

    return HTMLResponse(content=chatPage)

@agenticwAIfuApp.get("/character-cards", response_class=HTMLResponse)
def renderCharacterCards() -> HTMLResponse:

    fullCharacterCardHTML = ''

    characterCardFiles = glob.glob(str(CHARACTERS_DIR / "definitions" / "*.json"))
    for characterCardFile in characterCardFiles:
        characterCard = file_io.loadChar(characterCardFile)
        image_name = Path(characterCard.charImageFile.strip('"')).name

        # the problem is that these character cards need to be formatted appropriately with the  right html and css
        charHtml = f"""
        <div data-character-id="{characterCard.charName}" class="character-card">
            <img src="/character-images/{image_name}" alt="Character Image" class="character-image"/>
              <button class="character-edit-button" aria-label="Edit character">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4l10.5-10.5-4-4L4 16v4zM15.5 4.5l4 4 1.2-1.2a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.2 1.2z" />
                </svg>
            </button>
            <div class="character-name">{characterCard.charName}</div>
        </div>
        """;

        fullCharacterCardHTML += charHtml
    
    return HTMLResponse(content=fullCharacterCardHTML)

@agenticwAIfuApp.get("/loadout-cards", response_class=HTMLResponse)
def renderLoadoutCards() -> HTMLResponse:

    fullLoadoutCardHTML = ''

    loadoutCardFiles = glob.glob(str(LOADOUTS_DIR / "*.json"))
    for loadoutCardFile in loadoutCardFiles:
        loadoutCard = file_io.loadLoadout(loadoutCardFile)
        image_name = Path(loadoutCard.loadoutImageFile.strip('"')).name

        # the problem is that these loadout cards need to be formatted appropriately with the  right html and css
        loadoutHtml = f"""
        <div data-loadout-id="{loadoutCard.loadoutName}" class="loadout-card">
            <img src="/loadout-images/{image_name}" alt="Loadout Image" class="loadout-image"/>
              <button class="loadout-edit-button" aria-label="Edit loadout">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4l10.5-10.5-4-4L4 16v4zM15.5 4.5l4 4 1.2-1.2a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.2 1.2z" />
                </svg>
            </button>
            <div class="loadout-name">{loadoutCard.loadoutName}</div>
        </div>
        """;

        fullLoadoutCardHTML += loadoutHtml
    
    return HTMLResponse(content=fullLoadoutCardHTML)

def normalize_char_attribute(raw_attribute : dict) -> dict:
    data = dict(raw_attribute)

    if data.get("characterId") and not data.get("characterIds"):
        data["characterIds"] = [data.get("characterId")]
    elif data.get("characterName") and not data.get("characterNames"):
        data["characterNames"] = [data.get("characterName")]
    
    return data

def normalize(var):
    if isinstance(var, list):
        var = var[0]
    return var