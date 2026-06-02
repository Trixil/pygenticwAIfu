import json
import os
import shutil
from pathlib import Path

from ..core.paths import APP_DIR, CHARACTER_IMAGES_DIR, CHATS_DIR, LOADOUTS_DIR, CHARACTER_DEFINITIONS_DIR
from ..models import definitions

# this function is ass
def validateFilename(filename):
    forbidden = '<>:"\\|?*'
    if any(symbol in filename for symbol in forbidden):
        raise ValueError(f"WHY DID YOU NAME IT THAT REEEEEEEEEEEEEEEEE the filename is {filename}")

def saveChat(chatDict, chatFile=None, chatID=None):
    #validateFilename(chatFile)

    if chatID is not None and chatFile is None:
        chatFile = str(CHATS_DIR / f"{chatID}.json")
    elif chatFile is not None and chatID is not None:
        raise ValueError("pick one crodie")
        
    print("finna dump")
    with open(chatFile, "w", encoding="utf-8") as f:
        json.dump(chatDict, f, indent=2)
    print("dumped")

def loadChat(chatFile=None, chatID=None) -> definitions.chat:

    if chatID is not None and chatFile is None:
        chatFile = str(CHATS_DIR / f"{chatID}.json")
    elif chatFile is not None and chatID is not None:
        raise ValueError("pick one crodie")
    
    with open(chatFile, "r", encoding="utf-8") as file:
        fullChat = json.load(file)
    
    return definitions.chat.model_validate(fullChat)

def saveChar(charObject, charFile):

    imageFileSrc = Path(charObject.charImageFile)
    if not imageFileSrc.is_absolute():
        imageFileSrc = APP_DIR / imageFileSrc
    imageFileDest = CHARACTER_IMAGES_DIR / imageFileSrc.name

    if imageFileSrc.resolve() != imageFileDest.resolve():
        shutil.copyfile(imageFileSrc, imageFileDest)
    with open(charFile, "w", encoding="utf-8") as f:
        json.dump(charObject.model_dump(), f, indent=2)

def loadChar(charFile=None, charID=None) -> definitions.character:

    if charID is not None and charFile is None:
        charFile = str(CHARACTER_DEFINITIONS_DIR / f"{charID}.json")
    elif charFile is not None and charID is not None:
        raise ValueError("pick one crodie")

    with open(charFile, "r", encoding="utf-8") as file:
        character = json.load(file)

    return definitions.character.model_validate(character)

def saveLoadout(loadoutDict, loadoutFile):
    #loadoutFile = validateFilename(loadoutFile)
    with open(loadoutFile, "w", encoding="utf-8") as f:
        json.dump(loadoutDict, f, indent=2)

def loadLoadout(loadoutFile=None, loadoutID=None) -> definitions.agentLoadout:

    if loadoutID is not None and loadoutFile is None:
        loadoutFile = str(LOADOUTS_DIR / f"{loadoutID}.json")
    elif loadoutFile is not None and loadoutID is not None:
        raise ValueError("pick one crodie")
    
    with open(loadoutFile, "r", encoding="utf-8") as file:
        agentLoadout = json.load(file)
    
    return definitions.agentLoadout.model_validate(agentLoadout)


def deleteFile(filename):
    os.remove(filename)
