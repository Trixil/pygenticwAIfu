import glob
import shutil
import os

from pathlib import Path
from uuid import uuid4
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
    print("not validated uwu")
    if not file_io.validateFilename(characterName):
        return {"validFilename": False}
    print("validated uwu")

    CHARACTER_DEFINITIONS_DIR.mkdir(parents=True, exist_ok=True)
    CHARACTER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(characterImage.filename, flush=True)
    characterID = uuid4().hex

    imageExt = Path(characterImage.filename).suffix
    imageFilename = f"{characterID}{imageExt}"

    characterFile = CHARACTER_DEFINITIONS_DIR / f"{characterID}.json"
    print(str(characterFile))
    imageFileDest = CHARACTER_IMAGES_DIR / imageFilename
    print(str(imageFileDest))

    with imageFileDest.open("wb") as buffer:
        shutil.copyfileobj(characterImage.file, buffer)

    print("copied  theoretically")
    newCharacter = definitions.character(
        charName=characterName,
        charId=characterID,
        charNickname=nickname,
        charDesc=description,
        charScenario=scenario,
        charFile=str(Path("data") / "characters" / "definitions" / f"{characterID}.json"),
        charImageFile=str(Path("data") / "characters" / "images" / imageFilename)
    )

    file_io.saveChar(newCharacter, characterFile)

    return {
        "validFilename": True,
        "characterFile": str(newCharacter.charFile),
        "characterImageFile": str(newCharacter.charImageFile),
        "characterImageFilename": imageFilename,
        "characterImageUrl": f"/character-images/{imageFilename}",
        "characterID": characterID
    }

@router.post("/api/update-character")
def updateCharacter(
    characterName: str = Form(...),
    characterImage: UploadFile | None = File(None),
    nickname: str = Form(...),
    description: str = Form(...),
    scenario: str = Form(...),
    exampleDialogue: str = Form(""),
    characterID: str = Form(...),
    existingImageFile: str = Form("")
):
    print("you reached here")

    if not file_io.validateFilename(characterName):
        return {"validFilename": False}

    CHARACTER_DEFINITIONS_DIR.mkdir(parents=True, exist_ok=True)
    CHARACTER_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    characterCard = file_io.loadChar(charID=characterID)
    oldImageFilepath = characterCard.charImageFile

    has_new_image = (
        characterImage is not None
        and characterImage.filename is not None
        and characterImage.filename != ""
        and characterImage.size != 0
    )

    if has_new_image:
        if oldImageFilepath and os.path.exists(oldImageFilepath):
            os.remove(oldImageFilepath)

        imageExt = Path(characterImage.filename).suffix
        imageFilename = f"{characterID}{imageExt}"

        imageFileDest = CHARACTER_IMAGES_DIR / imageFilename

        with imageFileDest.open("wb") as buffer:
            shutil.copyfileobj(characterImage.file, buffer)

        characterImageFile = str(imageFileDest)

    else:
        if existingImageFile:
            imageFilename = Path(existingImageFile).name
            characterImageFile = str(CHARACTER_IMAGES_DIR / imageFilename)
        else:
            imageFilename = Path(oldImageFilepath).name
            characterImageFile = oldImageFilepath

    characterFile = CHARACTER_DEFINITIONS_DIR / f"{characterID}.json"

    updatedCharacter = definitions.character(
        charName=characterName,
        charId=characterID,
        charNickname=nickname,
        charDesc=description,
        charScenario=scenario,
        charExampleDialogue=exampleDialogue,
        charFile=str(characterFile),
        charImageFile=characterImageFile
    )

    file_io.saveChar(updatedCharacter, characterFile)

    return {
        "validFilename": True,
        "charName": characterName,
        "charImageFilename": imageFilename,
    }

@router.post("/add-character-card", response_class=HTMLResponse)
def addCharacter(characterName: str = Form(...),
                 characterID: str = Form(...)) -> HTMLResponse:
    
    characterCard = file_io.loadChar(charID=characterID)
    characterImageFile = Path(characterCard.charImageFile).name

    charHtml = f"""
        <div data-character-id="{characterCard.charId}" class="character-card">
            <img src="/character-images/{characterImageFile}" alt="Character Image" class="character-image"/>
              <button class="character-edit-button" aria-label="Edit character">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4l10.5-10.5-4-4L4 16v4zM15.5 4.5l4 4 1.2-1.2a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.2 1.2z" />
                </svg>
            </button>
            <div class="character-name">{characterName}</div>
        </div>
        """;

    return HTMLResponse(content=charHtml)

@router.post("/populate-character-pane")
async def populateCharacterPane(request: Request):
    data = await request.json()
    characterId = data["characterId"]
    
    characterCard = file_io.loadChar(charID=characterId)
    name = characterCard.charName
    nickname = characterCard.charNickname
    scenario = characterCard.charScenario
    description = characterCard.charDesc
    exampleDialogue = characterCard.charExampleDialogue
    imageFile = characterCard.charImageFile

    return({
        "name": name,
        "nickname": nickname,
        "scenario": scenario,
        "description": description,
        "exampleDialogue": exampleDialogue,
        "imageFile": imageFile
    })

@router.post("/select-character-for-chat")
async def renderChatCardOfCharacter(request: Request):

    data = await request.json()
    characterID = data["characterId"]
    characterCard = file_io.loadChar(charID=characterID)
    characterImageName = str(Path(characterCard.charImageFile).name)

    cardHtml = f"""
        <div class="selected-chat-card" data-chat-card-id={characterID}>
            <img src="/character-images/{characterImageName}"
                class="selected-chat-card-image">
            <span class="selected-chat-text">{characterCard.charName}</span>
        </div>
    """

    return {"cardHtml": cardHtml}

@router.get("/render-character-cards", response_class=HTMLResponse)
def renderCharacterCards() -> HTMLResponse:

    fullCharacterCardHTML = ''

    characterCardFiles = glob.glob(str(CHARACTER_DEFINITIONS_DIR / "*.json"))
    for characterCardFile in characterCardFiles:
        characterCard = file_io.loadChar(characterCardFile)
        image_name = Path(characterCard.charImageFile.strip('"')).name

        print(characterCard)
        # the problem is that these character cards need to be formatted appropriately with the  right html and css
        charHtml = f"""
        <div data-character-id="{characterCard.charId}" class="character-card">
            <img src="/character-images/{image_name}" alt="Character Image" class="character-image"/>
                <button
                    class="character-edit-button"
                    type="button"
                    aria-label="Edit character"
                    onclick="populateCharacterPane(this.closest('[data-character-id]')); document.getElementById('new-character-modal-toggle').checked = true;"
                >
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M4 20h4l10.5-10.5-4-4L4 16v4zM15.5 4.5l4 4 1.2-1.2a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.2 1.2z" />
                    </svg>
                </button>
            <div class="character-name">{characterCard.charName}</div>
        </div>
        """;

        fullCharacterCardHTML += charHtml
    
    return HTMLResponse(content=fullCharacterCardHTML)
