def buildMessageHTML(role: str, content: str):
    if role == "user":
        classString = "user"
    elif role == "assistant":
        classString = "character"
    else:
        raise ValueError(f"Unknown message role: {role}")

    return f"""
        <div class="{classString}-chat-bubble">
            <p class="{classString}-message">{content}</p>
        </div>
    """

def buildConvoHeadImageHTML(characterId: str, imageFile: str) -> str:
    return f"""
        <img class="convo-head-img" data-image-character-id="{characterId}" src="/character-images/{imageFile}">
    """
    