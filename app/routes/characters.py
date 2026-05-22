import glob
from pathlib import Path
import shutil

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse

from ..core.paths import CHARACTER_DEFINITIONS_DIR, CHARACTER_IMAGES_DIR
from ..models import definitions
from ..storage import file_io

router = APIRouter()

@router.post("/api/create-character")
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
    characterFile = CHARACTER_DEFINITIONS_DIR / (characterName + ".json")
    print("bruh")
    print("bruh")
    imageFileDest = CHARACTER_IMAGES_DIR / characterImage.filename

    with imageFileDest.open("wb") as buffer:
        shutil.copyfileobj(characterImage.file, buffer)
    
    newCharacter = definitions.character(
        charName=characterName,
        charNickname=nickname,
        charDesc=description,
        charScenario=scenario,
        charFile=str(Path("data") / "characters" / "definitions" / f"{characterName}.json"),
        charImageFile=str(Path("data") / "characters" / "images" / characterImage.filename)
    )

    file_io.saveChar(newCharacter, characterFile)
    print("bruh")
    return {"validFilename": True}

@router.post("/add-character-card", response_class=HTMLResponse)
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

@router.post("/select-character-for-chat")
async def renderChatCardOfCharacter(request: Request):

    data = await request.json()
    characterName = data["characterId"]
    characterCard = file_io.loadChar(str(CHARACTER_DEFINITIONS_DIR / (characterName + ".json")))
    characterImageName = str(Path(characterCard.charImageFile).name)

    cardHtml = f"""
        <div class="selected-chat-card" data-chat-card-id={characterName}>
            <img src="/character-images/{characterImageName}"
                class="selected-chat-card-image">
            <span class="selected-chat-text">{characterName}</span>
        </div>
    """

    return {"cardHtml": cardHtml}

@router.get("/character-cards", response_class=HTMLResponse)
def renderCharacterCards() -> HTMLResponse:

    fullCharacterCardHTML = ''

    characterCardFiles = glob.glob(str(CHARACTER_DEFINITIONS_DIR / "*.json"))
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
