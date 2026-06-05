import glob
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from ..core.paths import CHARACTER_IMAGES_DIR, CHATS_DIR, PAGES_DIR
from ..rendering import htmlHelpers
from ..routes.characters import renderCharacterCards
from ..routes.loadouts import renderLoadoutCards
from ..routes.chats import renderChatCards
from ..storage import file_io

router = APIRouter()

@router.get("/static")
def mainpage():
    landing_html = (PAGES_DIR / "landing.html").read_text(encoding="utf-8")
    character_cards_html = renderCharacterCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{CHARACTER_CARDS}}", character_cards_html)
    loadout_cards_html = renderLoadoutCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{LOADOUT_CARDS}}", loadout_cards_html)
    chat_cards_html = renderChatCards().body.decode("utf-8")
    landing_html = landing_html.replace("{{CHAT_CARDS}}", chat_cards_html)
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
        characterCard = file_io.loadChar(charID=characterID)
        
        imageFile = Path(characterCard.charImageFile).name
        convoHeadImgHTML += htmlHelpers.buildConvoHeadImageHTML(characterID, imageFile)

    convoHeadImgHTML += """
    </div>"""

    loadoutCard = file_io.loadLoadout(loadoutID=chatCard.chatAgentLoadout)
    loadoutName = loadoutCard.loadoutName
    loadoutID = loadoutCard.loadoutId

    characterCardsHTML = renderCharacterCards().body.decode("utf-8")
    loadoutCardsHTML = renderLoadoutCards().body.decode("utf-8")
    chatCardsHTML = renderChatCards().body.decode("utf-8")

    if chatCard.chatName:
        chatTitle = chatCard.chatName
    else:
        chatCardFiles = glob.glob(str(CHATS_DIR / "*.json"))
        newChatNumber = str(len(chatCardFiles) + 1)
        chatTitle = f"Untitled chat {newChatNumber}"
    
    chatPage = (PAGES_DIR / "chat.html").read_text(encoding="utf-8")
    chatPage = chatPage.replace("{{CHAT_TITLE}}", chatTitle)
    chatPage = chatPage.replace("{{CONVO_HEAD_CHARACTERS}}", convoHeadImgHTML)
    chatPage = chatPage.replace("{{LOADOUT_NAME}}", loadoutName)
    chatPage = chatPage.replace("{{LOADOUT_ID}}", loadoutID)
    chatPage = chatPage.replace("{{CONVO_MESSAGES}}", messageHTML)
    chatPage = chatPage.replace("{{CHARACTER_CARDS}}", characterCardsHTML)
    chatPage = chatPage.replace("{{LOADOUT_CARDS}}", loadoutCardsHTML)
    chatPage = chatPage.replace("{{CHAT_CARDS}}", chatCardsHTML)

    return HTMLResponse(content=chatPage)
