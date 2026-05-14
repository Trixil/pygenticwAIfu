import json
import os
from pydantic import BaseModel

try:
    from . import definitions
except ImportError:
    import definitions

def validateFilename(filename):
    forbidden = '<>:"/\\|?*'
    if any(symbol in filename for symbol in forbidden):
        return False
    return True

def saveChat(chatDict, chatFile):
    chatFile = validateFilename(chatFile)
    with open(chatFile, "w", encoding="utf-8") as f:
        json.dump(chatDict, f, indent=2)

def loadChat(chatFile) -> definitions.chat:
    with open(chatFile, "r", encoding="utf-8") as file:
        fullChat = json.load(file)
    
    return definitions.chat.model_validate(fullChat)

def saveChar(charObject, charFile):

    with open(charFile, "w", encoding="utf-8") as f:
        json.dump(charObject.model_dump(), f, indent=2)

def loadChar(charFile) -> definitions.character:
    with open(charFile, "r", encoding="utf-8") as file:
        character = json.load(file)
    
    return definitions.character.model_validate(character)

def saveLoadout(loadoutDict, loadoutFile):
    loadoutFile = validateFilename(loadoutFile)
    with open(loadoutFile, "w", encoding="utf-8") as f:
        json.dump(loadoutDict, f, indent=2)

def loadLoadout(loadoutFile) -> definitions.agentLoadout:
    with open(loadoutFile, "r", encoding="utf-8") as file:
        agentLoadout = json.load(file)
    
    return definitions.agentLoadout.model_validate(agentLoadout)

def deleteFile(filename):
    os.remove(filename)
