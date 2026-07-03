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

from ..core.paths import CHATS_DIR, CHARACTER_IMAGES_DIR, TEMPLATES_DIR, LOREBOOKS_DIR
from ..models import definitions
from ..rendering import htmlHelpers
from .lorebooks import appendLorebookEntry, nameAliasTypeTagLb, contentById
from ..storage import file_io
from ..utils.normalize import normalize
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
outputTable = {}
statusTable = {}
activationTable = {}
branchOutputs = {
    "upper": {},
    "lower": {},
}
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
    
    for msg in chatCard.messages:
        if msg.messageId == messageID:
            msg.content = newMessageContent
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
    global activationTable

    chatCard = file_io.loadChat(chatID=chatId)
    recursiveChatCard = chatCard

    loadoutID = chatCard.chatAgentLoadout
    loadoutCard = file_io.loadLoadout(loadoutID=loadoutID)
    
    agents = loadoutCard.loadoutAgents
    allAgentCards = agents
    startingAgents: list[definitions.agent] = []
    events = {}
    print("agents is")
    print(agents)
    #breakpoint()
    for agent in agents:
        agentId = agent.agentId
        outputTable[agentId] = ""
        events[agentId] = asyncio.Event()
        statusTable[agentId] = AgentStatus.WAITING
        activationTable[agentId] = True
        if agent.parents == []:
            startingAgents.append(agent)
    print(activationTable)
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

    #breakpoint()
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
        if agent.publish
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
    
    raise ValueError("Agent ID not found")

def getAgentNameByID(selectedAgentID):
    global allAgentCards

    for agent in allAgentCards:
        if agent.agentId == selectedAgentID:
            selectedAgent = getAgentByID(selectedAgentID)
            return selectedAgent.agentName
    
    raise ValueError("Agent ID not found")

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
    global branchOutputs
    global activationTable

    agentId = agent.agentId
    #if agent.agentName == "Arc Update Check":
        #breakpoint()
    
    statusTable[agentId] = AgentStatus.RUNNING
    writeStatusFile(statusTable)

    #if agent.agentName == "Arc Buffer":
        #breakpoint()
    
    print("activationTable")
    print(activationTable)
    #breakpoint()
    if (any(not activationTable[parentId] for parentId in agent.parents) and agent.parents and not agent.softActivation) or not activationTable[agentId]:
        activationTable[agentId] = False
        outputTable[agentId] = ""
    else:
        waitingParentIds = []

        for parentId in agent.parents:
            if statusTable[parentId] != AgentStatus.DONE:
                waitingParentIds.append(parentId)

        await asyncio.gather(
            *(events[parentId].wait() for parentId in waitingParentIds)
        )
        message = await generateLLMMessage(agent, events)
        outputTable[agentId] = message

    statusTable[agentId] = AgentStatus.DONE
    writeStatusFile(statusTable)
    events[agentId].set()

    waitingChildren: list[definitions.agent] = []

    if not agent.agentBranch:
        for childId in agent.children:

            if statusTable[childId] == AgentStatus.WAITING:
                waitingChildren.append(getAgentByID(childId))

        if not activationTable[agent.agentId]:
            activationTable.update({
                childAgentId: False
                for childAgentId in branch_children
                if not getAgentByID(childAgentId).softActivation
            })
                    
        if waitingChildren:
            await asyncio.gather(
                *(recursiveGenerate(child, events) for child in waitingChildren)
            )
    else:
        output = outputTable[agentId]

        branch_children = []
        branch_children.extend(agent.upperChildren)
        branch_children.extend(agent.lowerChildren)
        
        useLower = False
        useUpper = False

        if activationTable[agentId]:
            if agent.agentBranchUpperTrigger in output or "" == agent.agentBranchUpperTrigger:
                #branch_children.extend(agent.upperChildren)
                branchOutputs["upper"][agentId] = agent.agentBranchUpperInstructions.replace("{this_response}", output)
                useUpper = True

            if agent.agentBranchLowerTrigger in output or "" == agent.agentBranchLowerTrigger:
                #branch_children.extend(agent.lowerChildren)
                branchOutputs["lower"][agentId] = agent.agentBranchLowerInstructions.replace("{this_response}", output)
                useLower = True

            if not useUpper:
                branchOutputs["upper"][agentId] = ""
            if not useLower:
                branchOutputs["lower"][agentId] = ""
            
            #breakpoint()
            activationTable.update({
                childAgentId: False
                for childAgentId in agent.lowerChildren
                if not useLower and not getAgentByID(childAgentId).softActivation
            })

            activationTable.update({
                childAgentId: False
                for childAgentId in agent.upperChildren
                if not useUpper and not getAgentByID(childAgentId).softActivation
            })

        else:
            #branch_children.extend(agent.upperChildren)
            #branch_children.extend(agent.lowerChildren)
        
            activationTable.update({
                childAgentId: False
                for childAgentId in branch_children
                if not getAgentByID(childAgentId).softActivation
            })
        

        
        for child_id in branch_children:

            if statusTable[child_id] == AgentStatus.WAITING:
                waitingChildren.append(getAgentByID(child_id))

        #breakpoint()
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
    global branchOutputs

    #breakpoint()
    masterInput = ""
    lorebookFile = LOREBOOKS_DIR / f"{recursiveChatCard.chatID}_auto.json"

    #if agent.agentName == "Arc Draft":
        #breakpoint()
    
    instructionSet = agent.agentInstructions
    agentId = agent.agentId

    for parentId in agent.parents:
        parentCard = getAgentByID(parentId)
        parentSlug = getAgentSlugByID(parentId)

        parentOutput = None

        #/#/ NOT IMPLEMENTED: well, what if an agent is connected to both the upper and lower branch, huh?
        #if parentId == "563af260e37e40a3b0a306d92dd2db7b":
            #breakpoint()

        
        if not parentCard.agentBranch:
            parentOutput = outputTable[parentId]
        elif agentId in parentCard.upperChildren:
            parentOutput = branchOutputs["upper"][parentId]

        elif agentId in parentCard.lowerChildren:
            parentOutput = branchOutputs["lower"][parentId]

        else:
            raise ValueError("Child agent ID not found in upper or lower children of parent branching agent.")
        
        if parentOutput is not None:
            instructionSet = instructionSet.replace(
                f"{{{parentSlug}_output}}",
                parentOutput
            )

    if "{name-alias-type-tag-lb}" in instructionSet:
        if not lorebookFile.exists():
            file_io.saveLorebook(lorebookObject=definitions.lorebook(), lorebookFile=lorebookFile)
            nattLb = "EMPTY LOREBOOK"
        else:
            nattLb = nameAliasTypeTagLb(file_io.loadLorebook(lorebookFile=lorebookFile))
        
        instructionSet = instructionSet.replace(
            "{name-alias-type-tag-lb}",
            nattLb
        )

    masterInput += htmlHelpers.buildInstructionSection(instructionSet)

    if agent.characterInput:
        masterInput += characterInfoSection

    if agent.scenario:
        masterInput += characterScenarioSection

    if agent.carryOver:
        agentOutputsFile = CHATS_DIR / "agentOutputs" / f"{recursiveChatCard.chatID}.json"

        if not agentOutputsFile.exists():
            with open(agentOutputsFile, "w", encoding="utf-8") as f:
                pass
            carryOver = ""
        else:
            with open(agentOutputsFile, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if content:
                agentOutputs = json.loads(content)
                carryOver = agentOutputs.get(agent.carryOverAgentId, "")
            else:
                carryOver = ""

        masterInput += htmlHelpers.buildCarryoverSection(carryOver)


    openrouterMessages = [
        {
            "role": "system",
            "content": masterInput
        }
    ]

    pastMessageContent = ""

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

    errorFilePath = CHATS_DIR / "agentOutputs"/ f"{recursiveChatCard.chatID}" / "errorlog.txt"

    os.makedirs(os.path.dirname(errorFilePath), exist_ok=True)

    try:
        #breakpoint()
        openRouterMessages = [{"role": "system", "content": "repeat after me: bruh"}, {"role": "user", "content": "repeat after me: bruh"}]
        completion = await client.chat.completions.create(
            model=agent.agentLLMConfig.LLMName,
            messages=openrouterMessages,
            temperature=agent.agentLLMConfig.temp,
            top_p=agent.agentLLMConfig.topP,
            max_tokens=agent.agentLLMConfig.maxTokens
        )
#
        assistant_message = completion.choices[0].message.content
        #assistant_message = ""

        #if not assistant_message:
        #    raise AgentGenerationError(
        #        f"Agent {agent.agentName} returned an empty message."
        #    )
        
        if assistant_message is None:
            assistant_message = ""
        
        writeAgentOutputDebug(assistant_message, agent)
        writeSingleAgentOutput(assistant_message, agent)

        print(assistant_message)
        if agent.publish:
            finalMessage = assistant_message

        agentOutputsDir = CHATS_DIR / "agentOutputs"
        agentOutputsDir.mkdir(parents=True, exist_ok=True)
        if agent.writeLorebook:
            breakpoint()
            lorebookFile = LOREBOOKS_DIR / f"{recursiveChatCard.chatID}_auto.json"

            if lorebookFile.exists():
                lorebook = file_io.loadLorebook(lorebookFile=lorebookFile)
            else:
                lorebook = definitions.lorebook()
            
            lorebook = appendLorebookEntry(lorebook, assistant_message)
            file_io.saveLorebook(lorebook, lorebookFile)

            return "Successfully wrote to lorebook."
        
        elif agent.queryLorebook:
            lorebookFile = LOREBOOKS_DIR / f"{recursiveChatCard.chatID}_auto.json"
            if lorebookFile.exists():
                lorebook = file_io.loadLorebook(lorebookFile=lorebookFile)
            else:
                return "---NO LOREBOOK FOUND---"
            
            ids = [item.strip() for item in assistant_message.split(",")]
            return contentById(lorebook, ids)
        
        else:
            agentOutputsFile = agentOutputsDir / f"{recursiveChatCard.chatID}.json"

            if agentOutputsFile.exists():
                with open(agentOutputsFile, "r", encoding="utf-8") as f:
                    agentOutputs = json.load(f)
            else:
                agentOutputs = {}

            agentOutputs[agentId] = assistant_message

            with open(agentOutputsFile, "w", encoding="utf-8") as f:
                json.dump(agentOutputs, f, ensure_ascii=False, indent=2)

            return assistant_message

    except BadRequestError as e:
        errorString = f"Bad request: {e}"
        logError(errorString)
        raise AgentGenerationError(errorString)

    except RateLimitError as e:
        errorString = f"Rate limit error: {e}"
        logError(errorString)
        raise AgentGenerationError(errorString)

    except APIConnectionError as e:
        errorString = f"Connection error: {e}"
        logError(errorString)
        raise AgentGenerationError(errorString)

    except APIError as e:
        errorString = f"API error: {e}"
        logError(errorString)
        raise AgentGenerationError(errorString)

    except Exception as e:
        errorString = f"Unexpected error: {type(e).__name__}: {e}"
        logError(errorString)
        raise AgentGenerationError(errorString)

class AgentGenerationError(Exception):
    pass

def writeOpenRouterMessagesDebug(openrouterMessages, agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "agentOutputs"/ f"{recursiveChatCard.chatID}" / "debuginputs.txt"

    os.makedirs(os.path.dirname(filePath), exist_ok=True)

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

def logError(errorString):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "agentOutputs"/ f"{recursiveChatCard.chatID}" / "errorLog.txt"

    os.makedirs(os.path.dirname(filePath), exist_ok=True)

    with open(filePath, "a", encoding="utf-8") as file:
        file.write("\n")
        file.write("=" * 80)
        file.write("\n")
        file.write(f"Datetime: {timestamp}\n")
        file.write(errorString)
        file.write("=" * 80)
        file.write("\n\n")
        
def writeAgentOutputDebug(assistant_message, agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "agentOutputs"/ f"{recursiveChatCard.chatID}" / "debugoutputs.txt"

    os.makedirs(os.path.dirname(filePath), exist_ok=True)

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

def writeSingleAgentOutput(assistant_message, agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filePath = CHATS_DIR / "agentOutputs"/ f"{recursiveChatCard.chatID}" / f"{agent.agentName}.txt"

    os.makedirs(os.path.dirname(filePath), exist_ok=True)

    with open(filePath, "a", encoding="utf-8") as file:
        file.write("\n")
        file.write("=" * 80)
        file.write("\n")
        file.write(f"Datetime: {timestamp}\n")
        file.write("=" * 80)
        file.write("\n\n")

        file.write(assistant_message)
        file.write("\n\n")

    return filePath

def writeStatusFile(statusTable):
    statusLogFile = CHATS_DIR / "agentOutputs" / recursiveChatCard.chatID / "statusLog.txt"

    statusLogFile.parent.mkdir(parents=True, exist_ok=True)

    with open(statusLogFile, "a", encoding="utf-8") as f:
        f.write(f"""------------------------------------------------------""")
        for agentId, status in statusTable.items():
            f.write(f"""
                    {getAgentNameByID(agentId)}: {status.value}\n
                    """)






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