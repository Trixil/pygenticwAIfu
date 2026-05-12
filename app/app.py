from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field
import definitions
from contextlib import asynccontextmanager
import os
import time
import glob
import json
from pathlib import Path
import file_io

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
CHARACTERS_DIR = APP_DIR / "characters"
CHARACTER_IMAGES_DIR = CHARACTERS_DIR / "images"

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
    
    if not os.path.isdir("agent-loadouts"):
        os.mkdir("agent-loadouts")
    
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

@agenticwAIfuApp.get("/start-chat")
def startChat():
    return {"ok": True, "message": "bruh","connected": True, "reply": "yes"}

@agenticwAIfuApp.get("/check-status")
def checkStatus():
    return {"ok": True, "status": "online", "service": "chat"}

@agenticwAIfuApp.get("/static")
def mainpage():
    return FileResponse(STATIC_DIR / "landing.html")

@agenticwAIfuApp.get("/chat")
def chatpage():
    return FileResponse(STATIC_DIR / "chatpage.html")

@agenticwAIfuApp.get("/api/ping")
def pong():
    return {"ok": True, "message": "pong"}

@agenticwAIfuApp.get("/character-cards", response_class=HTMLResponse)
def renderCharacterCards() -> HTMLResponse:

    fullCharacterCardHTML = ''

    characterCardFiles = glob.glob(str(CHARACTERS_DIR / "definitions" / "*.json"))
    for characterCardFile in characterCardFiles:
        characterCard = file_io.loadChar(characterCardFile)
        image_name = Path(characterCard.charImageFile.strip('"')).name

        charHtml = f"""
        <div class="character-card">
            <img src="/character-images/{image_name}" alt="Character Image" />
            <div class="character-name">{characterCard.charName}</div>
        </div>
        """;

        fullCharacterCardHTML += charHtml
    
    return HTMLResponse(content=fullCharacterCardHTML)

def normalize_char_attribute(raw_attribute : dict) -> dict:
    data = dict(raw_attribute)

    if data.get("characterId") and not data.get("characterIds"):
        data["characterIds"] = [data.get("characterId")]
    elif data.get("characterName") and not data.get("characterNames"):
        data["characterNames"] = [data.get("characterName")]
    
    return data
