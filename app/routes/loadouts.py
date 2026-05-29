import glob
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..core.paths import LOADOUTS_DIR, TEMPLATES_DIR
from ..storage import file_io
from ..models import definitions

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

@router.get("/loadout-cards", response_class=HTMLResponse)
def renderLoadoutCards() -> HTMLResponse:

    fullLoadoutCardHTML = ''

    loadoutCardFiles = glob.glob(str(LOADOUTS_DIR / "*.json"))
    for loadoutCardFile in loadoutCardFiles:
        loadoutCard = file_io.loadLoadout(loadoutCardFile)
        image_name = Path(loadoutCard.loadoutImageFile.strip('"')).name

        # the problem is that these loadout cards need to be formatted appropriately with the  right html and css
        loadoutHtml = f"""
        <div data-loadout-id="{loadoutCard.loadoutName}" class="loadout-card" onclick="showLoadoutEditor(this)">
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
    print (allConfigsById)
    agentLoadout = definitions.agentLoadout()

    for agentName, agentConfig in allConfigsById.items():
        print(agentConfig)
        agentConfig = agentConfig["agentConfiguration"]
        agentLLMConfig = definitions.LLMConfig.model_validate(agentConfig["agentLLMConfig"])
        agentDict = {
            "agentName": agentName,
            "agentId": agentConfig["agentId"],
            "agentInstructions": agentConfig["agentInstructions"],
            "characterInput": agentConfig["characterInput"],
            "scenario": agentConfig["scenario"],
            "carryOver": agentConfig["carryOver"],
            "parents": agentConfig["parents"],
            "children": agentConfig["children"],
            "agentLLMConfig": agentConfig["agentLLMConfig"]
        }

        agent = definitions.agent.model_validate(agentDict)
        print(agent)
        agentLoadout.loadoutAgents.append(agent)

    print(agentLoadout)

@router.post("/render-agent-pane", response_class=HTMLResponse)
async def renderAgentPane(request: Request):
    data = await request.json()

    print("data is")
    print(data)
    agentConfig = data["agentConfig"]["agentConfiguration"]
    agentName = data["agentName"]

    agentPaneHTML = (TEMPLATES_DIR / "pages" / "loadoutPane.html").read_text(encoding="utf-8")

    agentPaneHTML = agentPaneHTML.replace("{{AGENT_NAME}}", agentName)
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_INSTRUCTIONS}}", agentConfig["agentInstructions"])
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM}}", agentConfig["agentLLMConfig"]["LLMName"])
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM_TEMP}}", str(agentConfig["agentLLMConfig"]["temp"]))
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM_MAX_TOKENS}}", str(agentConfig["agentLLMConfig"]["maxTokens"]))
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_LLM_TOP_P}}", str(agentConfig["agentLLMConfig"]["topP"]))
    agentPaneHTML = agentPaneHTML.replace("{{AGENT_PAST_MESSAGE_COUNT}}", "0")
    
    useCharacterInput = "checked" if agentConfig["characterInput"] else ""
    useScenario = "checked" if agentConfig["scenario"] else ""
    useCarryOver = "checked" if agentConfig["carryOver"] else ""
    agentPaneHTML = agentPaneHTML.replace("{{USE_CHARACTER_CARDS}}", useCharacterInput)
    agentPaneHTML = agentPaneHTML.replace("{{USE_CARRYOVER}}", useCarryOver)
    agentPaneHTML = agentPaneHTML.replace("{{USE_SCENARIO}}", useScenario)
    
    return HTMLResponse(content=agentPaneHTML)