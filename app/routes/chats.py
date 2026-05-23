import glob

from pathlib import Path
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi import Request

from ..core.paths import CHATS_DIR, CHARACTER_IMAGES_DIR
from ..models import definitions
from ..rendering import htmlHelpers
from ..storage import file_io
from ..utils.normalize import normalize

router = APIRouter()

@router.post("/start-new-chat")
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
        "chatFile": f"data/chats/{chatID}.json",
        "chatAgentLoadout": loadoutId,
        "chatCharacters": characterIds,
        "messages": []
    }

    print("chatDict is", chatDict)
    file_io.saveChat(chatDict, str(CHATS_DIR / f"{chatID}.json"))
    return {"chatID": chatID}

@router.post("/api/save-message")
async def saveMessage(chatMessageInput: str = Form(...), 
                    chatId: str = Form(...),
                    role: str = Form(...),
                    messageId: str = Form(...)):
    
    chatFile = str(CHATS_DIR / f"{chatId}.json")
    chatCard = file_io.loadChat(chatFile=chatFile)
    chatMessages = chatCard.messages

    print("role is " + role)
    
    # /#/# USER NAME NOT IMPLEMENTED YET
    newMessage = definitions.message.model_validate({
        "role": role,
        "sender": "Himothy NOT IMPLEMENTED YET",
        "content": chatMessageInput,
        "messageId": messageId
    })
    
    chatCard.messages.append(newMessage)
    
    file_io.saveChat(chatCard.model_dump(), chatFile)

@router.post("/render-new-message", response_class=HTMLResponse)
def renderNewMessage(chatMessageInput: str = Form(...),
                    role: str = Form(...)):
    messageHTML = htmlHelpers.buildMessageHTML(role, chatMessageInput)
    return HTMLResponse(content=messageHTML)

@router.post("/render-convo-head-image", response_class=HTMLResponse)
async def renderConvoHeadImage(request: Request):
    data = await request.json()
    characterID = data["characterId"]
    characterImageFiles = glob.glob(
        str(CHARACTER_IMAGES_DIR / f"{characterID}.*")
    )

    if not characterImageFiles:
        raise FileNotFoundError(f"No image found for {characterID}")
    
    imageFile = Path(characterImageFiles[0]).name
    html = htmlHelpers.buildConvoHeadImageHTML(characterID, imageFile)
    return HTMLResponse(content=html)

@router.post("/continue-convo-with-characters")
async def continueConvoWithCharacters(request: Request):

    data = await request.json()
    selectedCharacterIDs = data["selectedCharacterIds"]
    chatID = data["chatId"]

    chatFile = str(CHATS_DIR / f"{chatID}.json")
    chatCard = file_io.loadChat(chatFile=chatFile)
    chatCard.chatCharacters = selectedCharacterIDs

    file_io.saveChat(chatCard.model_dump(), chatFile)

@router.post("/save-edited-user-message")
async def saveEditedUserMessage(request: Request):
    data = await request.json()
    newMessageContent = data["newMessageContent"]
    chatID = data["chatId"]
    messageID = data["messageId"]

    chatCard = file_io.loadChat(chatID=chatID)

    print("newMessageContent" + newMessageContent)
    print("chatID" + chatID)
    print("messageID" + messageID)
    
    for msg in chatCard.messages:
        print("msg is " + msg.content)
        if msg.messageId == messageID:
            print("oldmessage is " + msg.content)
            msg.content = newMessageContent
            print("newmessage is " + msg.content)
            break

    file_io.saveChat(chatCard.model_dump(), chatID=chatID)
