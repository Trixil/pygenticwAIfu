import numpy
import glob
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi import HTTPException

from ..core.paths import LOADOUTS_DIR, TEMPLATES_DIR
from ..storage import file_io
from ..models import definitions
from ..rendering import htmlHelpers, loadoutCardImages

router = APIRouter()

@router.post("/select-loadout-for-chat")
async def renderChatCardOfLoadout(request: Request):

    data = await request.json()
    loadoutName = data["loadoutId"]
    loadoutCard = file_io.loadLoadout(str(LOADOUTS_DIR / (loadoutName + ".json")))
    loadoutImageName = str(Path(loadoutCard.loadoutImageFile).name)

    cardHtml = f"""
        <div class="selected-chat-card" data-loadout-card-id="{loadoutName}">
            <img src="/loadout-images/{loadoutImageName}"
                class="selected-chat-card-image">
            <span class="selected-chat-text">{loadoutName}</span>
        </div>
    """

    return {"cardHtml": cardHtml}

@router.get("/render-loadout-cards", response_class=HTMLResponse)
def renderLoadoutCards() -> HTMLResponse:

    fullLoadoutCardHTML = ''

    loadoutCardFiles = glob.glob(str(LOADOUTS_DIR / "*.json"))
    for loadoutCardFile in loadoutCardFiles:
        loadoutCard = file_io.loadLoadout(loadoutCardFile)
        image_name = Path(loadoutCard.loadoutImageFile.strip('"')).name

        # the problem is that these loadout cards need to be formatted appropriately with the  right html and css
        loadoutHtml = f"""
        <div data-loadout-id="{loadoutCard.loadoutId}" class="loadout-card" onclick="openSavedLoadout(this)">
            <img src="/loadout-images/{image_name}" alt="Loadout Image" class="loadout-image"/>
              <button class="loadout-edit-button" aria-label="Edit loadout">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 20h4l10.5-10.5-4-4L4 16v4zM15.5 4.5l4 4 1.2-1.2a1.4 1.4 0 0 0 0-2l-2-2a1.4 1.4 0 0 0-2 0l-1.2 1.2z" />
                </svg>
            </button>
            <div class="loadout-name">{loadoutCard.loadoutName}</div>
        </div>
        """;

        fullLoadoutCardHTML += loadoutHtml
    
    return HTMLResponse(content=fullLoadoutCardHTML)


@router.post("/save-loadout-configuration")
async def saveLoadoutConfiguration(request: Request):
    data = await request.json()

    allConfigsById = data["allConfigsById"]
    loadoutID = data["loadoutId"]

    agentLoadout = definitions.agentLoadout()
    agentLoadout.loadoutId = loadoutID

    for agentID, agentConfigWrapper in allConfigsById.items():
        agentName = agentConfigWrapper["agentName"]
        agentConfig = agentConfigWrapper["agentConfiguration"]

        layout = agentConfigWrapper.get("layout", {
            "x": 0,
            "y": 0
        })

        agentDict = {
            "agentName": agentName,
            "agentId": agentID,
            "agentInstructions": agentConfig["agentInstructions"],
            "characterInput": agentConfig["characterInput"],
            "scenario": agentConfig["scenario"],
            "carryOver": agentConfig["carryOver"],
            "parents": agentConfig["parentsId"],
            "children": agentConfig["childrenId"],
            "agentLLMConfig": agentConfig["agentLLMConfig"],
            "layout": layout
        }

        agent = definitions.agent.model_validate(agentDict)
        agentLoadout.loadoutAgents.append(agent)

    agentLoadout.loadoutImageFile = loadoutCardImages.create_loadout_quilt_image(
        loadoutID,
        str(LOADOUTS_DIR / "images")
    )

    file_io.saveLoadout(
        agentLoadout.model_dump(),
        str(LOADOUTS_DIR / f"{loadoutID}.json")
    )

    return {"status": "saved"}

@router.post("/render-agent-pane", response_class=HTMLResponse)
async def renderAgentPane(request: Request):
    data = await request.json()

    print("data is")
    print(data)
    agentConfig = data["agentConfig"]["agentConfiguration"]
    agentName = data["agentName"]
    agentNamesByID = data["agentNamesById"]

    agentPaneHTML = (TEMPLATES_DIR / "pages" / "loadoutPane.html").read_text(encoding="utf-8")

    agentPaneHTML = agentPaneHTML.replace("{{AGENT_NAME}}", agentName)
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_INSTRUCTIONS}}", agentConfig["agentInstructions"])
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM}}", agentConfig["agentLLMConfig"]["LLMName"])
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM_TEMP}}", str(agentConfig["agentLLMConfig"]["temp"]))
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM_MAX_TOKENS}}", str(agentConfig["agentLLMConfig"]["maxTokens"]))
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM_TOP_P}}", str(agentConfig["agentLLMConfig"]["topP"]))
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_PAST_MESSAGE_COUNT}}", str(agentConfig["agentLLMConfig"]["pastMessageCount"]))
    
    useCharacterInput = "checked" if agentConfig["characterInput"] else ""
    useScenario = "checked" if agentConfig["scenario"] else ""
    useCarryOver = "checked" if agentConfig["carryOver"] else ""
    agentPaneHTML = agentPaneHTML.replace("{{USE_CHARACTER_CARDS}}", useCharacterInput)
    agentPaneHTML = agentPaneHTML.replace("{{USE_CARRYOVER}}", useCarryOver)
    agentPaneHTML = agentPaneHTML.replace("{{USE_SCENARIO}}", useScenario)
    
    inputHTML = ""
    for inputId in agentConfig["parentsId"]:
        inputName = agentNamesByID[inputId]
        agentSlug = inputName.replace(" ", "")
        inputHTML += htmlHelpers.buildOutputListEntryHTML(agentSlug)
    
    agentPaneHTML = agentPaneHTML.replace("{{INPUT_LIST}}", inputHTML)

    return HTMLResponse(content=agentPaneHTML)


@router.post("/render-agent-card", response_class=HTMLResponse)
async def renderAgentCard(request: Request):
    data = await request.json()

    print("data is")
    print(data)
    agentConfig = data["agentConfig"]["agentConfiguration"]
    agentID = agentConfig["agentId"]
    agentName = data["agentName"]

    agentCardHTML = (TEMPLATES_DIR / "pages" / "agentCard.html").read_text(encoding="utf-8")

    agentInstructions = agentConfig["agentInstructions"]
    endIdx = min(250, len(agentInstructions) - 1)
    agentInstructionsCropped = agentInstructions[:endIdx]

    agentCardHTML = agentCardHTML.replace("{{AGENT_NAME}}", agentName)
    agentCardHTML = agentCardHTML.replace("{{AGENT_ID}}", agentID)
    agentCardHTML = agentCardHTML.replace("{{AGENT_INSTRUCTIONS_CROPPED}}", agentInstructionsCropped)
    agentCardHTML = agentCardHTML.replace("{{AGENT_LLM}}", agentConfig["agentLLMConfig"]["LLMName"])
    agentCardHTML = agentCardHTML.replace("{{AGENT_PAST_MESSAGE_COUNT}}", agentConfig["agentLLMConfig"]["pastMessageCount"])
    agentCardHTML = agentCardHTML.replace("{{AGENT_TOKENS}}", numpy.ceil(agentInstructions/4))
    
    useCharacterInput = "agent-card__button--checked" if agentConfig["characterInput"] else ""
    useScenario = "agent-card__button--checked" if agentConfig["scenario"] else ""
    useCarryOver = "agent-card__button--checked" if agentConfig["carryOver"] else ""
    agentCardHTML = agentCardHTML.replace("{{USE_CHARACTER_CARDS}}", useCharacterInput)
    agentCardHTML = agentCardHTML.replace("{{USE_CARRYOVER}}", useCarryOver)
    agentCardHTML = agentCardHTML.replace("{{USE_SCENARIO}}", useScenario)
    
    return HTMLResponse(content=agentCardHTML)

@router.get("/loadout-configuration/{loadout_id}")
async def getLoadoutConfiguration(loadout_id: str):
    loadoutFile = LOADOUTS_DIR / f"{loadout_id}.json"

    print(loadoutFile)
    if not loadoutFile.exists():
        raise HTTPException(status_code=404, detail="Loadout not found")

    return file_io.loadLoadout(str(loadoutFile)).model_dump()

# agentName: "",
# agentConfiguration: {
#     agentId: agentId,
#     agentInstructions: "",
#     characterInput: false,
#     scenario: false,
#     carryOver: false,
#     pastMessageCount: 0,
#     parents: [],
#     children: [],
#     agentLLMConfig: {
#         LLMName: "",
#         temp: 1,
#         maxTokens: 4000,
#         topP: 1
#     }
# }