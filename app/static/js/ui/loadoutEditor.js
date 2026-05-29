async function showLoadoutEditor(loadoutCardElement)
{
    document.querySelector(".layout").classList.toggle("config-expand-hide");
    document.querySelector(".layout").classList.toggle("config-expand-widen");
    
    document.querySelector("#character-cards").classList.toggle("hidden", true);
    document.querySelector("#loadout-cards").classList.toggle("hidden", true);
    document.querySelector(".loadout-editor").classList.toggle("hidden");
    
    let loadoutId =  loadoutCardElement.dataset.loadoutId;

    if (loadoutId === "NEW LOADOUT")
    {
        loadoutId = crypto.randomUUID().replace(/-/g, "");
    }

    document.querySelector(".loadout-editor").setAttribute("data-loadout-id", loadoutId);
}

const editorState = {
    allConfigsById: {},
    allChildren: {},
    isDraggingAgent: false,
    isDraggingLine: false,
    draggedAgent: null,
    draggedLine: null,
    activeSvg: null,
    xOffset: 0,
    yOffset: 0
};

function registerPaneNameEditor(editorPane, agentId, agent) {
    const nameInput = editorPane.querySelector(".loadout-editor-pane-name-input");
    const overviewName = agent.querySelector(".agent-card__name");

    nameInput.addEventListener("pointerdown", function (event) {
        event.stopPropagation();
    });

    nameInput.addEventListener("click", function (event) {
        event.stopPropagation();

        nameInput.readOnly = false;
        nameInput.focus();
        nameInput.select();
    });

    function commitNameChange() {
        const newName = nameInput.value.trim();

        if (newName === "") {
            nameInput.value =
                editorState.allConfigsById[agentId].agentName ||
                overviewName.textContent.trim();

            nameInput.readOnly = true;
            return;
        }

        editorState.allConfigsById[agentId].agentName = newName;

        overviewName.textContent = newName;

        nameInput.value = newName;
        nameInput.readOnly = true;
    }

    nameInput.addEventListener("blur", commitNameChange);

    nameInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            nameInput.blur();
        }

        if (event.key === "Escape") {
            event.preventDefault();

            nameInput.value =
                editorState.allConfigsById[agentId].agentName ||
                overviewName.textContent.trim();

            nameInput.readOnly = true;
            nameInput.blur();
        }
    });
}

function registerLoadoutPaneControls(editorPane, agentId, agent) {
    const agentConfig = editorState.allConfigsById[agentId];
    const config = agentConfig.agentConfiguration;

    // ---------- hide pane ----------
    const hideButton = editorPane.querySelector(".loadout-editor-pane-hide-button");

    hideButton.addEventListener("click", function (event) {
        event.stopPropagation();

        editorPane.classList.add("pane-hidden");

        editorPane.addEventListener("transitionend", function handleTransitionEnd(event) {
            if (event.propertyName !== "transform") return;
            editorPane.remove();
        }, { once: true });
    });

    // ---------- tabs ----------
    const tabs = editorPane.querySelectorAll(".loadout-editor-pane--tab");

    tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            const tabName = tab.dataset.tab;
            editorPane.dataset.activeTab = tabName;
        });
    });

    // ---------- instructions ----------
    const instructionsTextarea = editorPane.querySelector(".loadout-editor-instructions-textarea");

    instructionsTextarea.addEventListener("input", function () {
        config.agentInstructions = instructionsTextarea.value;
                        agent.querySelector(".token-bubble")
                    .querySelector(".agent-card__meta-text")
                    .textContent = `~${Math.ceil(instructionsTextarea.value.length / 4)}`;
    });

    let instructionsIntervalId = null;

    instructionsTextarea.addEventListener("focus", function () {
        if (instructionsIntervalId !== null) return;

        instructionsIntervalId = setInterval(function () {
            const instructions = instructionsTextarea.value;

            if (instructions.length < 250) {
                agent.querySelector(".agent-card__instructions").textContent = instructions;
                agent.querySelector(".token-bubble")
                    .querySelector(".agent-card__meta-text")
                    .textContent = `~${Math.ceil(instructions.length / 4)}`;

                editorState.allConfigsById[agentId]
                    .agentConfiguration
                    .agentInstructions = instructions;
            }
        }, 2000);
    });

    instructionsTextarea.addEventListener("blur", function () {
        if (instructionsIntervalId !== null) {
            clearInterval(instructionsIntervalId);
            instructionsIntervalId = null;
        }
    });

    // ---------- LLM settings ----------
    const modelNameInput = editorPane.querySelector("#loadout-model-name");
    const temperatureInput = editorPane.querySelector("#loadout-temperature");
    const topPInput = editorPane.querySelector("#loadout-top-p");
    const maxTokensInput = editorPane.querySelector("#loadout-max-tokens");

    modelNameInput.addEventListener("input", function () {
    config.agentLLMConfig.LLMName = modelNameInput.value;

    agent.querySelector(".model-bubble")
        .querySelector(".agent-card__meta-text")
        .textContent = modelNameInput.value;
        agent.querySelector(".agent-card__meta-text").textContent = modelNameInput.value;
    });

    temperatureInput.addEventListener("input", function () {
        config.agentLLMConfig.temp = Number(temperatureInput.value);
    });

    topPInput.addEventListener("input", function () {
        config.agentLLMConfig.topP = Number(topPInput.value);
    });

    maxTokensInput.addEventListener("input", function () {
        config.agentLLMConfig.maxTokens = Number(maxTokensInput.value);
    });

    // ---------- messages ----------
    const pastMessagesInput = editorPane.querySelector("#loadout-past-messages");

    pastMessagesInput.addEventListener("input", function () {
        config.pastMessageCount = Number(pastMessagesInput.value);
    });

    // ---------- input checkboxes ----------
    const characterCardsCheckbox = editorPane.querySelector("#loadout-use-character-cards");
    const scenarioCheckbox = editorPane.querySelector("#loadout-use-scenario");
    const carryOverCheckbox = editorPane.querySelector("#loadout-use-carryover");

    const characterInputButton = agent.querySelector(".agent-character-input");
    const scenarioButton = agent.querySelector(".agent-scenario");
    const carryOverButton = agent.querySelector(".agent-carryover");

    characterCardsCheckbox.addEventListener("change", function () {
        config.characterInput = characterCardsCheckbox.checked;

        characterInputButton.classList.toggle(
            "agent-card__button--checked",
            characterCardsCheckbox.checked
        );
    });

    scenarioCheckbox.addEventListener("change", function () {
        config.scenario = scenarioCheckbox.checked;

        scenarioButton.classList.toggle(
            "agent-card__button--checked",
            scenarioCheckbox.checked
        );
    });

    carryOverCheckbox.addEventListener("change", function () {
        config.carryOver = carryOverCheckbox.checked;

        carryOverButton.classList.toggle(
            "agent-card__button--checked",
            carryOverCheckbox.checked
        );
    });

    registerPaneNameEditor(editorPane, agentId, agent);

}

async function showAgentPane(agent) {
    const agentId = agent.dataset.agentId;
    const agentName = agent.querySelector(".agent-card__name").textContent.trim();

    if (!editorState.allConfigsById[agentId]) {
        editorState.allConfigsById[agentId] = createDefaultAgentConfig(agentId);
    }

    const agentConfig = editorState.allConfigsById[agentId];

    const loadoutId = document.querySelector(".loadout-editor").dataset.loadoutId;

    const response = await fetch("/render-agent-pane", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            loadoutId: loadoutId,
            agentConfig: agentConfig,
            agentName: agentName
        })
    });

    if (!response.ok) {
        console.error("Failed to render agent pane");
        return;
    }

    const html = await response.text();

    const wrapper = document.createElement("div");
    wrapper.innerHTML = html.trim();

    const editorPane = wrapper.firstElementChild;

    editorPane.classList.add("pane-hidden");

    document.querySelector(".loadout-editor").appendChild(editorPane);

    registerLoadoutPaneControls(editorPane, agentId, agent);
    
    requestAnimationFrame(function () {
        requestAnimationFrame(function () {
            editorPane.classList.remove("pane-hidden");
        });
    });

    const tabButtons = editorPane.querySelectorAll(".loadout-editor-pane--tab");

    tabButtons.forEach(button => {
        button.addEventListener("click", function () {
            editorPane.dataset.activeTab = button.dataset.tab;
        });
    });

    const hideButton = editorPane.querySelector(".loadout-editor-pane-hide-button");

    hideButton.addEventListener("click", function () {
        editorPane.classList.add("pane-hidden");

        editorPane.addEventListener("transitionend", function handleTransitionEnd(event) {
            if (event.propertyName !== "transform") return;

            editorPane.remove();
        }, { once: true });
    });
}
    // check allConfigsById for a config with agentid
    // if it exists, pull the configuration
    // send the agent configuration to the /render-loadout-pane
    // it loads the agent config into a single card
    // retrieves the loadoutPane template
    // does a replace on all of the different properties of loadoutPane from the agnet config
    // saves it and sends it back
    // showAgentPane js frontend adds it as a sibling to the end of the loadout-editor view
    // immediately applies style.transformX(-100%) to it


function registerAgent(agent) {
    const agentId = agent.dataset.agentId;

    // Prevent duplicate event listeners if this agent gets registered twice.
    if (agent.dataset.registered === "true") return;
    agent.dataset.registered = "true";

    // Create config if this agent does not already have one.
    if (!editorState.allConfigsById[agentId]) {
        editorState.allConfigsById[agentId] = createDefaultAgentConfig(agentId);
    }

    // Create children tracking if missing.
    if (!editorState.allChildren[agentId]) {
        editorState.allChildren[agentId] = new Set();
    }

    const agentOutput = agent.querySelector(".agent-port--out");
    const agentInput = agent.querySelector(".agent-port--in");
    const svgList = agent.querySelector(".wire-layer");

    const checkboxButtons = agent.querySelectorAll(".agent-card__button--flat");

    const carryOver = agent.querySelector(".agent-carryover");
    const scenario = agent.querySelector(".agent-scenario");
    const characterInput = agent.querySelector(".agent-character-input");

    carryOver.addEventListener("click", function (event) {
        event.stopPropagation();

        carryOver.classList.toggle("agent-card__button--checked");

        const isChecked = carryOver.classList.contains("agent-card__button--checked");

        editorState.allConfigsById[agentId]
            .agentConfiguration
            .carryOver = isChecked;

        const paneCarryOver = document.querySelector("#loadout-use-carryover");

        if (paneCarryOver) {
            paneCarryOver.checked = isChecked;
        }
    });

    scenario.addEventListener("click", function (event) {
        event.stopPropagation();

        scenario.classList.toggle("agent-card__button--checked");

        const isChecked = scenario.classList.contains("agent-card__button--checked");

        editorState.allConfigsById[agentId]
            .agentConfiguration
            .scenario = isChecked;

        const paneScenario = document.querySelector("#loadout-use-scenario");

        if (paneScenario) {
            paneScenario.checked = isChecked;
        }
    });

    characterInput.addEventListener("click", function (event) {
        event.stopPropagation();

        characterInput.classList.toggle("agent-card__button--checked");

        const isChecked = characterInput.classList.contains("agent-card__button--checked");

        editorState.allConfigsById[agentId]
            .agentConfiguration
            .characterInput = isChecked;

        const paneCharacterInput = document.querySelector("#loadout-use-character-cards");

        if (paneCharacterInput) {
            paneCharacterInput.checked = isChecked;
        }
    });

    carryOver.addEventListener("pointerdown", function (event) {
        event.stopPropagation();
    });

    scenario.addEventListener("pointerdown", function (event) {
        event.stopPropagation();
    });

    characterInput.addEventListener("pointerdown", function (event) {
        event.stopPropagation();
    });

    agent.addEventListener("pointerdown", function (downEvent) {
        const outRect = agentOutput.getBoundingClientRect();

        const clickedOutput =
            downEvent.clientX >= outRect.left &&
            downEvent.clientX <= outRect.right &&
            downEvent.clientY >= outRect.top &&
            downEvent.clientY <= outRect.bottom;

        if (clickedOutput) return;

        editorState.isDraggingAgent = true;
        editorState.draggedAgent = agent;

        const rect = agent.getBoundingClientRect();

        editorState.xOffset = downEvent.clientX - rect.left;
        editorState.yOffset = downEvent.clientY - rect.top;

        agent.setPointerCapture(downEvent.pointerId);
    });

    const agentNameElement = agent.querySelector(".agent-card__name");
    agentNameElement.addEventListener("pointerdown", function (event) {
        event.stopPropagation();
    });

    agentNameElement.addEventListener("pointerup", function (event) {
        event.stopPropagation();
    });

    agentNameElement.addEventListener("click", function (event) {
        event.stopPropagation();
        showAgentPane(agent);
    });

    agentOutput.addEventListener("pointerdown", function (downEvent) {
        downEvent.stopPropagation();

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

        editorState.draggedLine = line;
        editorState.activeSvg = svgList;
        editorState.isDraggingLine = true;

        const outRect = agentOutput.getBoundingClientRect();
        const svgRect = editorState.activeSvg.getBoundingClientRect();

        const startX = outRect.left + outRect.width / 2 - svgRect.left;
        const startY = outRect.top + outRect.height / 2 - svgRect.top;

        const endX = downEvent.clientX - svgRect.left;
        const endY = downEvent.clientY - svgRect.top;

        line.setAttribute("x1", startX);
        line.setAttribute("y1", startY);
        line.setAttribute("x2", endX);
        line.setAttribute("y2", endY);
        line.setAttribute("stroke", "white");
        line.setAttribute("stroke-width", "2");
        line.setAttribute("data-agent-start", agentId);

        editorState.activeSvg.appendChild(line);
    });

    agentInput.addEventListener("pointerup", function () {
        if (
            editorState.isDraggingLine &&
            editorState.draggedLine &&
            editorState.activeSvg
        ) {
            const startAgentId = editorState.draggedLine.getAttribute("data-agent-start");
            const endAgentId = agentId;

            if (
                startAgentId === endAgentId ||
                isLoop(startAgentId, endAgentId, editorState.allChildren)
            ) {
                editorState.draggedLine.remove();
                editorState.draggedLine = null;
                editorState.isDraggingLine = false;
                editorState.activeSvg = null;
                return;
            }

            const svgRect = editorState.activeSvg.getBoundingClientRect();
            const inRect = agentInput.getBoundingClientRect();

            const startX = Number(editorState.draggedLine.getAttribute("x1"));
            const startY = Number(editorState.draggedLine.getAttribute("y1"));

            const endX = inRect.left + inRect.width / 2 - svgRect.left;
            const endY = inRect.top + inRect.height / 2 - svgRect.top;

            const connectorLine = document.createElementNS("http://www.w3.org/2000/svg", "line");

            connectorLine.setAttribute("x1", startX);
            connectorLine.setAttribute("y1", startY);
            connectorLine.setAttribute("x2", endX);
            connectorLine.setAttribute("y2", endY);
            connectorLine.setAttribute("stroke", "white");
            connectorLine.setAttribute("stroke-width", "2");
            connectorLine.setAttribute("data-agent-start", startAgentId);
            connectorLine.setAttribute("data-agent-end", endAgentId);

            editorState.activeSvg.appendChild(connectorLine);

            editorState.allChildren[startAgentId].add(endAgentId);

            editorState.allConfigsById[startAgentId]
                .agentConfiguration
                .children
                .add(endAgentId);

            editorState.allConfigsById[endAgentId]
                .agentConfiguration
                .parents
                .add(startAgentId);

            editorState.draggedLine.remove();
            editorState.draggedLine = null;
            editorState.isDraggingLine = false;
            editorState.activeSvg = null;
        }
    });

}

function createDefaultAgentConfig(agentId) {
    return {
        agentName: "",
        agentConfiguration: {
            agentId: agentId,
            agentInstructions: "",
            characterInput: false,
            scenario: false,
            carryOver: false,
            pastMessageCount: 0,
            parents: [],
            children: [],
            agentLLMConfig: {
                LLMName: "",
                temp: 1,
                maxTokens: 4000,
                topP: 1
            }
        }
    };
}

async function startLoadoutEditor() {
    const saveButton = document.querySelector(".loadout-save-button");

    const allAgents = [...document.querySelectorAll("[data-agent-id]")];

    allAgents.forEach(registerAgent);

    document.addEventListener("pointermove", function (moveEvent) {
        if (!editorState.isDraggingAgent && !editorState.isDraggingLine) return;

        if (editorState.isDraggingAgent && editorState.draggedAgent) {
            const parentRect = editorState.draggedAgent.offsetParent.getBoundingClientRect();

            editorState.draggedAgent.style.left =
                `${moveEvent.clientX - parentRect.left - editorState.xOffset}px`;

            editorState.draggedAgent.style.top =
                `${moveEvent.clientY - parentRect.top - editorState.yOffset}px`;
        }

        if (
            editorState.isDraggingLine &&
            editorState.draggedLine &&
            editorState.activeSvg
        ) {
            const svgRect = editorState.activeSvg.getBoundingClientRect();

            editorState.draggedLine.setAttribute("x2", moveEvent.clientX - svgRect.left);
            editorState.draggedLine.setAttribute("y2", moveEvent.clientY - svgRect.top);
        }
    });

    document.addEventListener("pointerup", function () {
        if (editorState.draggedLine != null) {
            editorState.draggedLine.remove();
        }

        editorState.isDraggingAgent = false;
        editorState.draggedAgent = null;

        editorState.isDraggingLine = false;
        editorState.draggedLine = null;
        editorState.activeSvg = null;
    });

    async function saveLoadoutConfiguration() {
        const loadoutEditor = document.querySelector(".loadout-editor");
        const loadoutId = loadoutEditor.dataset.loadoutId;

        const payload = Object.fromEntries(
            Object.entries(editorState.allConfigsById).map(([agentId, agentConfig]) => [
                agentId,
                {
                    ...agentConfig,
                    agentConfiguration: {
                        ...agentConfig.agentConfiguration,

                        parents: [...agentConfig.agentConfiguration.parents],
                        children: [...agentConfig.agentConfiguration.children],

                        agentLLMConfig: {
                            ...agentConfig.agentConfiguration.agentLLMConfig
                        }
                    }
                }
            ])
        );

        const response = await fetch("/save-loadout-configuration", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                loadoutId: loadoutId,
                allConfigsById: payload
            })
        });

        if (!response.ok) {
            console.error("Failed to save loadout configuration");
            return;
        }

        const result = await response.json();
        console.log("Saved loadout configuration:", result);
    }

    saveButton.addEventListener("pointerdown", saveLoadoutConfiguration);
}

function isLoop(source, destination, kindergarten)
{
    const destinationChildren = [...(kindergarten[destination] ?? [])];
    if (destinationChildren.includes(source))
    {
        return true;
    }

    const hasLoop = destinationChildren.some(function (child) {
        return isLoop(source, child, kindergarten);
    });

    return hasLoop;

}
// agent config created
// add eventlistener for all buttons
// eventListener sets the agent config value


// how to check if it loops?
// have inputs and outputs for each agent. then, when node C tries to connect to A, it should not be allowed because A is one of C's children, or C is one of A's parents.
// first build the inputs list.
// every time a line is connected, extract data-agent-start-id, query it in the parent inputs json, and add data-agent-end-id to its kids.
// EVERY time you try to connect a line to another agent (from C to A), call isLoop(A, C)
// 1. check if C's direct children include A.
// 1a. if so, then return true, is loopable.
// 1b. if not, then loop through each of C's kids calling isLoop(A, [C child])