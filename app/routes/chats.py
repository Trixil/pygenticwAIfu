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

from ..core.paths import CHATS_DIR, CHARACTER_IMAGES_DIR, TEMPLATES_DIR
from ..models import definitions
from ..rendering import htmlHelpers
from ..storage import file_io
from ..utils.normalize import normalize

router = APIRouter()
outputTable = {}
statusTable = {}
allAgentCards = {}
messages = []

recursiveChatCard = []
characterInfo = []
scenarioInfo = []
characterInfoSection = []
characterScenarioSection = []
messageCards = []

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

@router.post("/generate-assistant-message")
async def generateAssistantMessage(chatMessageInput: str = Form(...), 
                    chatId: str = Form(...),
                    role: str = Form(...),
                    messageId: str = Form(...)):
        
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
    characterInfo = []
    characterScenario = []
    for characterId in recursiveChatCard.chatCharacters:
        character = file_io.loadChar(charID=characterId)
        characterInfo += f"""
            ---------- CHARACTER DESCRIPTION: {character.charName} ---------- 
            {character.charDesc}"""
        
        characterScenario += f"""
            ---------- SCENARIO FOR CHARACTER: {character.charName} ---------- 
            {character.charScenario}"""
    
    messageCards = recursiveChatCard.messages

    characterInfoSection = htmlHelpers.buildCharacterInfoSection(characterInfo)
    characterScenarioSection = htmlHelpers.buildScenarioInfoSection(characterScenario)

    asyncio.run(kickOffGeneration(startingAgents, agents, events))

async def watchStartingAgents(startingAgents, events):
    await asyncio.gather(
        *(recursiveGenerate(x, events) for x in startingAgents)
    )        

async def kickOffGeneration(startingAgents, events):
    await asyncio.create_task(watchStartingAgents(startingAgents, events))

def getAgentByID(selectedAgentID):
    global allAgentCards

    for agent in allAgentCards:
        if agent.agentId == selectedAgentID:
            return agent
    
    raise ValueError("Agent not found")

def getAgentSlugByID(selectedAgentID):
    global allAgentCards

    for agent in allAgentCards:
        if agent.agentId == selectedAgentID:
            selectedAgent = getAgentByID(allAgentCards, selectedAgentID)
            return selectedAgent.agentName.replace(" ", "")
    
    raise ValueError("Agent not found")

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
    
    events[agent.agentId].set()

    waitingChildren: list[definitions.agent] = []
    for childId in agent.children:
        if statusTable[childId] == AgentStatus.WAITING:
            waitingChildren.append(getAgentByID(childId))
    
    if waitingChildren:
        await asyncio.gather(
            *(recursiveGenerate(x, events) for x in waitingChildren)
        )
    

class AgentStatus(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    DONE = "done"

async def generateLLMMessage(agent, events):

    global characterInfoSection
    global characterScenarioSection
    global recursiveChatCard

    masterInput = ""

    # insert llm call here
    instructionSet = agent.agentInstructions
    for parentId in agent.parents:
        parent = getAgentByID(parentId)
        parentSlug = getAgentSlugByID(parentId)

        instructionSet.replace(f"{{{parentSlug}}}", parent.agentInstructions)

    ### INSTRUCTIONS
    masterInput += htmlHelpers.buildInstructionSection(instructionSet)

    ### CHARACTER INFO
    characterCards: list[definitions.character] = []
    for characterId in recursiveChatCard.chatCharacters:
        character = file_io.loadChar(charID=characterId)
        characterCards.append(character)
    
    if agent.characterInput:
        masterInput += characterInfoSection

    if agent.scenario:
        masterInput += characterScenarioSection
    
    if agent.carryOver:
        agentOutputsFile = str(CHATS_DIR / "agentOutputs" / f"{recursiveChatCard.chatID}")
        with open(agentOutputsFile, "r", encoding="utf-8") as f:
            agentOutputs = json.load(agentOutputsFile)

        carryOver = agentOutputs.get(agent.agentId, [])

        masterInput += htmlHelpers.buildCarryoverSection(agentOutputs[agent.agentId]) if carryOver != [] else ""

    systemMessage = masterInput
    openrouterMessages = [
        {
            "role": "system",
            "content": systemMessage
        }
    ]

    pastMessageContent = ""
    userMessage = ""
    if agent.pastMessageCount > 0:
        for messageNumber in range(len(messageCards) - 1, max(len(messageCards) - agent.pastMessageCount - 1, 0), -1):
            role = "User" if messageCards[messageNumber].role == "user" else "Narrator"
            content = messageCards[messageNumber].content
            pastMessageContent += f"""
            {role}: {content}"""

        userMessage = htmlHelpers.buildMessageLogSection(pastMessageContent)
        openrouterMessages.append(
        {
            "role": "user",
            "content": userMessage
        })
    
    writeOpenRouterMessagesDebug(openrouterMessages, agent)
    
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    try:
        completion = await client.chat.completions.create(
            model=agent.agentLLMConfig.LLMName,
            messages=openrouterMessages,
            temperature=agent.agentLLMConfig.temp,
            top_p = agent.agentLLMConfig.topP,
            max_tokens = agent.agentLLMConfig.maxTokens
        )

        assistant_message = completion.choices[0].message.content
        print(assistant_message)
    except BadRequestError as e:
        print("Bad request:")
        print(e)

    except RateLimitError as e:
        print("Rate limit error:")
        print(e)

    except APIConnectionError as e:
        print("Connection error:")
        print(e)

    except APIError as e:
        print("API error:")
        print(e)

    except Exception as e:
        print("Unexpected error:")
        print(type(e).__name__)
        print(e)
    
    events[agent.agentId].set()
    statusTable[agent.agentId] = AgentStatus.DONE


def writeOpenRouterMessagesDebug(openrouterMessages, agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "debugoutputs.txt"

    with open(filePath, "a", encoding="utf-8") as file:
        file.write("\n")
        file.write("=" * 80)
        file.write("\n")
        file.write(f"Datetime: {timestamp}\n")
        file.write(f"Agent ID: {agent.agentId}\n")
        file.write("=" * 80)
        file.write("\n\n")

        file.write(json.dumps(openrouterMessages, indent=2, ensure_ascii=False))
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