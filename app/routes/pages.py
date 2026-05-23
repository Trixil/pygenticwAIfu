import glob
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from ..core.paths import CHARACTER_IMAGES_DIR, CHATS_DIR, PAGES_DIR
from ..rendering import htmlHelpers
from ..routes.characters import renderCharacterCards
from ..routes.loadouts import renderLoadoutCards
from ..storage import file_io

router = APIRouter()

@router.get("/static")
def mainpage():
    landing_html = (PAGES_DIR / "landing.html").read_text(encoding="utf-8")
    character_cards_html = renderCharacterCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{CHARACTER_CARDS}}", character_cards_html)
    loadout_cards_html = renderLoadoutCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{LOADOUT_CARDS}}", loadout_cards_html)
    return HTMLResponse(content=landing_html)

@router.get("/chat")
def chatpage():
    return FileResponse(PAGES_DIR / "chatpage.html")

@router.get("/chat/{chatID}", response_class=HTMLResponse)
async def serveNewChat(chatID: str):

    chatCard = file_io.loadChat(chatFile=str(CHATS_DIR / f"{chatID}.json"))
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
            str(CHARACTER_IMAGES_DIR / f"{characterID}.*")
        )

        if not characterImageFiles:
            raise FileNotFoundError(f"No image found for {characterID}")
        
        imageFile = Path(characterImageFiles[0]).name
        convoHeadImgHTML += htmlHelpers.buildConvoHeadImageHTML(characterID, imageFile)

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

    characterCardsHTML = renderCharacterCards().body.decode("utf-8")

    chatPage = (PAGES_DIR / "chat.html").read_text(encoding="utf-8")
    chatPage = chatPage.replace("{{CONVO_HEAD_CHARACTERS}}", convoHeadImgHTML)
    chatPage = chatPage.replace("{{PIPELINE_BUBBLE}}", pipelineBubbleHTML)
    chatPage = chatPage.replace("{{CONVO_MESSAGES}}", messageHTML)
    chatPage = chatPage.replace("{{CHARACTER_CARDS}}", characterCardsHTML)

    return HTMLResponse(content=chatPage)
