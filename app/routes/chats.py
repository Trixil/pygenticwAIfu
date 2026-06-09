import glob
import asyncio
import json
import os

from openai import OpenAI
from openai import AsyncOpenAI
from openai import APIError, APIConnectionError, RateLimitError, BadRequestError
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi import Request
from enum import Enum
from uuid import uuid4

from ..core.paths import CHATS_DIR, CHARACTER_IMAGES_DIR, TEMPLATES_DIR
from ..models import definitions
from ..rendering import htmlHelpers
from ..storage import file_io
from ..utils.normalize import normalize
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
outputTable = {}
statusTable = {}
allAgentCards = {}
messages = []

recursiveChatCard = []
characterInfo = ""
scenarioInfo = ""
characterInfoSection = ""
characterScenarioSection = ""
messageCards = []

finalMessage = None

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@router.get("/chat-cards", response_class=HTMLResponse)
def renderChatCards() -> HTMLResponse:

    fullChatCardHTML = ''

    chatCardFiles = glob.glob(str(CHATS_DIR / "*.json"))
    for chatCardFile in chatCardFiles:
        chatCard = file_io.loadChat(chatFile=chatCardFile)
        chatID = chatCard.chatID

        characterCard = file_io.loadChar(charID=chatCard.chatCharacters[0])
        image_name = Path(characterCard.charImageFile).name
        chatName = chatCard.chatName

        chatHtml = htmlHelpers.buildChatCard(image_name, chatName, chatID)
        fullChatCardHTML += chatHtml
    
    return HTMLResponse(content=fullChatCardHTML)


@router.post("/start-new-chat")
async def startNewChat(request: Request):
    data = await request.json()
    characterIds = data["characterIds"]
    loadoutId = normalize(data["loadoutId"])

    chatFiles = glob.glob(
        str(CHATS_DIR / "*.json")
    )

    chatID = uuid4().hex

    chatDict = {
        "chatName": "",
        "chatID": chatID,
        "chatFile": f"data/chats/{chatID}.json",
        "chatAgentLoadout": loadoutId,
        "chatCharacters": characterIds,
        "messages": []
    }

    file_io.saveChat(chatDict, str(CHATS_DIR / f"{chatID}.json"))
    return {"chatID": chatID}

@router.post("/api/save-message")
async def saveMessage(request: Request):
    data = await request.json()

    content = data["content"]
    chatId = data["chatId"]
    role = data["role"]
    messageId = data["messageId"]
    
    chatFile = str(CHATS_DIR / f"{chatId}.json")
    chatCard = file_io.loadChat(chatFile=chatFile)
    
    # /#/# USER NAME NOT IMPLEMENTED YET
    newMessage = definitions.message.model_validate({
        "role": role,
        "sender": "Himothy NOT IMPLEMENTED YET",
        "content": content,
        "messageId": messageId
    })
    
    chatCard.messages.append(newMessage)
    
    file_io.saveChat(chatCard.model_dump(), chatFile)



@router.post("/render-new-message", response_class=HTMLResponse)
async def renderNewMessage(request: Request):
    data = await request.json()

    role = data["role"]
    content = data["content"]

    messageHTML = htmlHelpers.buildMessageHTML(role, content)

    return HTMLResponse(content=messageHTML)

@router.post("/render-convo-head-image", response_class=HTMLResponse)
async def renderConvoHeadImage(request: Request):
    data = await request.json()
    characterID = data["characterId"]
    imageFile = file_io.loadChar(charID=characterID).charImageFile
    imageFile = Path(imageFile).name
    
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

@router.post("/continue-convo-with-loadout")
async def continueConvoWithCharacters(request: Request):

    data = await request.json()
    selectedLoadoutId = data["selectedLoadoutId"]
    chatID = data["chatId"]

    chatFile = str(CHATS_DIR / f"{chatID}.json")
    chatCard = file_io.loadChat(chatFile=chatFile)
    print(chatCard)
    chatCard.chatAgentLoadout = selectedLoadoutId

    file_io.saveChat(chatCard.model_dump(), chatFile)

@router.post("/save-chat-title")
async def saveChatTitle(request: Request):
    data = await request.json()
    chatID = data["chatId"]
    chatTitle = data["chatTitle"]

    chatCard = file_io.loadChat(chatID=chatID)
    chatCard.chatName = chatTitle;
    file_io.saveChat(chatCard.model_dump(), chatID=chatID)

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

@router.post("/generate-assistant-message", response_class=HTMLResponse)
async def generateAssistantMessage(request: Request):
    data = await request.json()

    chatId = data["chatId"]
    global characterInfo
    global characterScenario
    global characterInfoSection
    global characterScenarioSection
    global messageCards
    global allAgentCards
    global recursiveChatCard
    global outputTable

    chatCard = file_io.loadChat(chatID=chatId)
    recursiveChatCard = chatCard

    loadoutID = chatCard.chatAgentLoadout
    loadoutCard = file_io.loadLoadout(loadoutID=loadoutID)
    
    agents = loadoutCard.loadoutAgents
    allAgentCards = agents
    startingAgents: list[definitions.agent] = []
    events = {}
    for agent in agents:
        outputTable[agent.agentId] = ""
        events[agent.agentId] = asyncio.Event()
        statusTable[agent.agentId] = AgentStatus.WAITING
        if agent.parents == []:
            startingAgents.append(agent)
    
    if startingAgents == {}:
        raise ValueError("where the parent at crodie")
    
    ### CHARACTER INFO
    characterInfo = ""
    characterScenario = ""
    for characterId in recursiveChatCard.chatCharacters:
        character = file_io.loadChar(charID=characterId)
        characterInfo += f"""
            ---------- CHARACTER DESCRIPTION: {character.charName} ---------- 
            {character.charDesc}"""
        
    # #/#/ NOT IMPLEMENTED YET: character-specific scenario
    # characterScenario += f"""
    #     ---------- SCENARIO FOR CHARACTER: {character.charName} ---------- 
    #     {character.charScenario}"""

    character = file_io.loadChar(charID=recursiveChatCard.chatCharacters[0])
    characterScenario += f"""
        ---------- SCENARIO ---------- 
        {character.charScenario}"""
    
    messageCards = recursiveChatCard.messages

    characterInfoSection = htmlHelpers.buildCharacterInfoSection(characterInfo)
    characterScenarioSection = htmlHelpers.buildScenarioInfoSection(characterScenario)

    generationOutcome = await runGeneration(startingAgents, events)
    if generationOutcome["success"]:
        return HTMLResponse(content=generationOutcome["message"])

async def runGeneration(startingAgents, events):
    global outputTable

    tasks = [
        asyncio.create_task(recursiveGenerate(agent, events))
        for agent in startingAgents
    ]

    try:
        await asyncio.gather(*tasks)

    except AgentGenerationError as e:
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "success": False,
            "message": "",
            "error": str(e)
        }

    finalAgents = [
        agent for agent in allAgentCards
        if agent.children == []
    ]

    if len(finalAgents) != 1:
        return {
            "success": False,
            "message": "",
            "error": f"Expected exactly one final narration agent, found {len(finalAgents)}."
        }

    finalAgent = finalAgents[0]

    return {
        "success": True,
        "message": outputTable[finalAgent.agentId],
        "error": ""
    }

def getAgentByID(selectedAgentID):
    global allAgentCards

    for agent in allAgentCards:
        if agent.agentId == selectedAgentID:
            return agent
    
    raise ValueError("Agent ID not found")

def getAgentSlugByID(selectedAgentID):
    global allAgentCards

    for agent in allAgentCards:
        if agent.agentId == selectedAgentID:
            selectedAgent = getAgentByID(selectedAgentID)
            return selectedAgent.agentName.replace(" ", "")
    
    raise ValueError("Agent slug not found")

def getAgentIDByName(selectedAgentName):
    global allAgentCards

    for agent in allAgentCards:
        if agent.agentName == selectedAgentName:
            return agent.agentId
    
    raise ValueError("Agent name not found")

async def waiter(key, events):
    await events[key].wait()
    
async def waitForParents(tasks):
    await asyncio.gather(*tasks)

async def recursiveGenerate(agent, events):
    global statusTable
    global outputTable

    statusTable[agent.agentId] = AgentStatus.RUNNING

    waitingParentIds = []

    for parentId in agent.parents:
        if statusTable[parentId] != AgentStatus.DONE:
            waitingParentIds.append(parentId)

    await asyncio.gather(
        *(events[parentId].wait() for parentId in waitingParentIds)
    )

    message = await generateLLMMessage(agent, events)

    outputTable[agent.agentId] = message
    statusTable[agent.agentId] = AgentStatus.DONE
    events[agent.agentId].set()

    waitingChildren: list[definitions.agent] = []

    print("agentId is ")
    print(agent.agentId)
    print(agent.agentName)

    for childId in agent.children:
        print("childId is " + childId)

        if statusTable[childId] == AgentStatus.WAITING:
            waitingChildren.append(getAgentByID(childId))

    if waitingChildren:
        await asyncio.gather(
            *(recursiveGenerate(child, events) for child in waitingChildren)
        )

class AgentStatus(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    DONE = "done"

async def generateLLMMessage(agent, events):
    global characterInfoSection
    global characterScenarioSection
    global recursiveChatCard
    global outputTable

    masterInput = ""

    instructionSet = agent.agentInstructions

    for parentId in agent.parents:
        parentSlug = getAgentSlugByID(parentId)
        instructionSet = instructionSet.replace(
            f"{{{parentSlug}_output}}",
            outputTable[parentId]
        )
        
    masterInput += htmlHelpers.buildInstructionSection(instructionSet)

    if agent.characterInput:
        masterInput += characterInfoSection

    if agent.scenario:
        masterInput += characterScenarioSection

    if agent.carryOver:
        agentOutputsFile = CHATS_DIR / "agentOutputs" / f"{recursiveChatCard.chatID}.json"
        if agentOutputsFile.exists():
            with open(agentOutputsFile, "r", encoding="utf-8") as f:
                agentOutputs = json.load(f)

            carryOver = agentOutputs.get(agent.carryOverAgent, [])

            if carryOver:
                masterInput += htmlHelpers.buildCarryoverSection(carryOver)


    openrouterMessages = [
        {
            "role": "system",
            "content": masterInput
        }
    ]

    pastMessageContent = ""

    print("agent.pastMessageCount")
    print(agent.pastMessageCount)
    print("messageCards")
    print(messageCards)
    if agent.pastMessageCount > 0:
        recentMessages = messageCards[-agent.pastMessageCount:]

        for messageCard in recentMessages:
            role = "User" if messageCard.role == "user" else "Narrator"
            content = messageCard.content
            pastMessageContent += f"\n\n# {role}: {content}\n\n"
        
        openrouterMessages.append(
            {
                "role": "user",
                "content": htmlHelpers.buildMessageLogSection(pastMessageContent)
            }
        )
    
    writeOpenRouterMessagesDebug(openrouterMessages, agent)

    try:
        completion = await client.chat.completions.create(
            model=agent.agentLLMConfig.LLMName,
            messages=openrouterMessages,
            temperature=agent.agentLLMConfig.temp,
            top_p=agent.agentLLMConfig.topP,
            max_tokens=agent.agentLLMConfig.maxTokens
        )

        assistant_message = completion.choices[0].message.content

        if not assistant_message:
            raise AgentGenerationError(
                f"Agent {agent.agentName} returned an empty message."
            )
        
        writeAgentOutputDebug(assistant_message, agent)

        print(assistant_message)
        if agent.children == []:
            finalMessage = assistant_message

        agentOutputsDir = CHATS_DIR / "agentOutputs"
        agentOutputsDir.mkdir(parents=True, exist_ok=True)

        agentOutputsFile = agentOutputsDir / f"{recursiveChatCard.chatID}.json"

        if agentOutputsFile.exists():
            with open(agentOutputsFile, "r", encoding="utf-8") as f:
                agentOutputs = json.load(f)
        else:
            agentOutputs = {}

        agentOutputs[agent.agentId] = assistant_message

        with open(agentOutputsFile, "w", encoding="utf-8") as f:
            json.dump(agentOutputs, f, ensure_ascii=False, indent=2)
        
        return assistant_message

    except BadRequestError as e:
        raise AgentGenerationError(f"Bad request: {e}")

    except RateLimitError as e:
        raise AgentGenerationError(f"Rate limit error: {e}")

    except APIConnectionError as e:
        raise AgentGenerationError(f"Connection error: {e}")

    except APIError as e:
        raise AgentGenerationError(f"API error: {e}")

    except Exception as e:
        raise AgentGenerationError(f"Unexpected error: {type(e).__name__}: {e}")

class AgentGenerationError(Exception):
    pass

def writeOpenRouterMessagesDebug(openrouterMessages, agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "debuginputs.txt"

    with open(filePath, "a", encoding="utf-8") as file:
        file.write("\n")
        file.write("=" * 80)
        file.write("\n")
        file.write(f"Datetime: {timestamp}\n")
        file.write(f"Agent ID: {agent.agentId}\n")
        file.write("=" * 80)
        file.write("\n\n")

        file.write(json.dumps(openrouterMessages[0], indent=2, ensure_ascii=False))
        file.write("\n\n")

    return filePath

def writeAgentOutputDebug(assistant_message, agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "debugoutputs.txt"

    with open(filePath, "a", encoding="utf-8") as file:
        file.write("\n")
        file.write("=" * 80)
        file.write("\n")
        file.write(f"Datetime: {timestamp}\n")
        file.write(f"Agent ID: {agent.agentId}\n")
        file.write(f"Agent Name: {agent.agentName}\n")
        file.write("Debug Type: Agent Output\n")
        file.write("=" * 80)
        file.write("\n\n")

        file.write(assistant_message)
        file.write("\n\n")

    return filePath











    # load chat card
    # from this, load agent loadout
    # find the agent that has no parents
    # query the api for this agent
    # store this output into a DTO
    # iterate over all of the children simultaneously, querying each of them too provided that all of their parents have an output stored in the DTO



    # startingAgents = {A, B}
    # A, B, ... H: notSelected state
    # simul recursiveGenerate(A, B)
    # A: A set to selected
    # A: queries A for response
    # A: A set to finished
    # A: get list of notSelected children
    # A: recursiveGenerate(C)
    # C: 
    # C: C set to selected
    # C: queries C for response