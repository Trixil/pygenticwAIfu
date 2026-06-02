from uuid import uuid4

def buildMessageHTML(role: str, content: str):
    if role == "user":
        classString = "user"
    elif role == "assistant":
        classString = "character"
    else:
        raise ValueError(f"Unknown message role: {role}")

    messageId = uuid4().hex
    
    return f"""
    <div class="{classString}-chat-bubble" data-message-id="{messageId}">
        <div class="message-controls">
            <button class="message-edit-button" type="button" aria-label="Edit message" onclick="editMessage(this)">
                <svg class="message-edit-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4z" />
                    <path d="M13.5 6.5l4 4" />
                </svg>
            </button>
        </div>

        <p class="{classString}-message">{content}</p>
    </div>
"""

def buildConvoHeadImageHTML(characterId: str, imageFile: str) -> str:
    return f"""
        <img class="convo-head-img" data-image-character-id="{characterId}" src="/character-images/{imageFile}">
    """

def buildOutputListEntryHTML(agentSlug: str):
    return f"""
    <button class="loadout-editor-output-chip" type="button">{{{agentSlug}_output}}</button>
    """

def buildInstructionSection(instructions: str):
    return f"""
    --------------- AGENT INSTRUCTIONS ---------------
    You must follow all of these instructions exactly.

    {instructions}
    """

def buildCharacterInfoSection(characterInfo: str):
    return f"""
    --------------- CHARACTER INFORMATION ---------------
    These are details on all of the character(s) in the chat.

    {characterInfo}
    """

def buildScenarioInfoSection(scenarioInfo: str):
    return f"""
    --------------- SCENARIO INFORMATION ---------------
    The fictional scenario that this chat occurs in.

    {scenarioInfo}
    """

def buildCarryoverSection(carryover: str):
    return f"""
    --------------- PREVIOUS OUTPUT ---------------
    The output that you generated last turn.

    {carryover}
    """

def buildMessageLogSection(pastMessageContent: str):
    return f"""
    --------------- MESSAGE LOG ---------------

    {pastMessageContent}
    """