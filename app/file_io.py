import json
import os
from pydantic import BaseModel
import shutil
from pathlib import Path

try:
    from . import definitions
except ImportError:
    import definitions

APP_DIR = Path(__file__).resolve().parent

def validateFilename(filename):
    forbidden = '<>:"\\|?*'
    if any(symbol in filename for symbol in forbidden):
        raise ValueError(f"WHY DID YOU NAME IT THAT REEEEEEEEEEEEEEEEE the filename is {filename}")

def saveChat(chatDict, chatFile):
    validateFilename(chatFile)

    print("finna dump")
    with open(chatFile, "w", encoding="utf-8") as f:
        json.dump(chatDict, f, indent=2)
    print("dumped")

def loadChat(chatFile) -> definitions.chat:
    with open(chatFile, "r", encoding="utf-8") as file:
        fullChat = json.load(file)
    
    return definitions.chat.model_validate(fullChat)

def saveChar(charObject, charFile):

    imageFileSrc = Path(charObject.charImageFile)
    imageFileDest = APP_DIR / "characters" / "images" / imageFileSrc.name

    shutil.copyfile(imageFileSrc, imageFileDest)
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
