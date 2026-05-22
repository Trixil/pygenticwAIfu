import glob
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..core.paths import LOADOUTS_DIR
from ..storage import file_io

router = APIRouter()

@router.post("/select-loadout-for-chat")
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

@router.get("/loadout-cards", response_class=HTMLResponse)
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
