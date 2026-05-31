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

    function resetNameInput() {
        nameInput.value =
            editorState.allConfigsById[agentId].agentName ||
            overviewName.textContent.trim();

        nameInput.readOnly = true;
    }

    function commitNameChange() {
        const newName = nameInput.value.trim().replace(/\s{2,}/g, " ");
        const currentName =
            editorState.allConfigsById[agentId].agentName ||
            overviewName.textContent.trim();

        if (newName === "") {
            resetNameInput();
            return;
        }

        const duplicateNameExists = Object.entries(editorState.allConfigsById)
            .some(([id, config]) => {
                return id !== agentId && config.agentName === newName;
            });

        if (duplicateNameExists) {
            showToast("Two agents can't have the same name! Get creative, BAKA~!");
            resetNameInput();
            return;
        }

        const oldName = editorState.allConfigsById[agentId].agentName;
        editorState.allConfigsById[agentId].agentName = newName;
        overviewName.textContent = newName;

        nameInput.value = newName;
        nameInput.readOnly = true;

        editorState.allConfigsById[agentId].agentConfiguration.childrenId.forEach(function (agentChildId) {
            const childConfig = editorState.allConfigsById[agentChildId].agentConfiguration;
            const parentNameIdx = childConfig.parents.indexOf(oldName);

            if (parentNameIdx !== -1) {
                childConfig.parents[parentNameIdx] = newName;
            }
        });
    }

    nameInput.addEventListener("blur", commitNameChange);

    nameInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            nameInput.blur();
        }

        if (event.key === "Escape") {
            event.preventDefault();
            resetNameInput();
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
    const agentPastMessagesInput = agent.querySelector(".agent-card__chat-count-input");

    function normalizePastMessageCount(value) {
        const number = Number(value);

        if (!Number.isFinite(number) || number < 0) {
            return 0;
        }

        return Math.floor(number);
    }

    function setPastMessageCount(value) {
        const pastMessageCount = normalizePastMessageCount(value);

        config.pastMessageCount = pastMessageCount;

        pastMessagesInput.value = pastMessageCount;
        agentPastMessagesInput.value = pastMessageCount;
    }

    setPastMessageCount(config.pastMessageCount);

    pastMessagesInput.addEventListener("input", function () {
        setPastMessageCount(pastMessagesInput.value);
    });

    agentPastMessagesInput.addEventListener("input", function () {
        setPastMessageCount(agentPastMessagesInput.value);
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

    const agentNamesById = {};
    document.querySelectorAll(".agent-card").forEach(function (thisAgent) {
        const agentId = thisAgent.dataset.agentId;
        const agentName = thisAgent
            .querySelector(".agent-card__name")
            .textContent
            .trim();

        agentNamesById[agentId] = agentName;
    });

    const response = await fetch("/render-agent-pane", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            loadoutId: loadoutId,
            agentConfig: agentConfig,
            agentName: agentName,
            agentNamesById: agentNamesById
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

    editorPane.setAttribute("data-selected-agent-id", agent.dataset.agentId);

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

            const endAgentName = agent
                .querySelector(".agent-card__name")
                .textContent
                .trim();

            const startAgent = document.querySelector(`[data-agent-id="${startAgentId}"]`);

            const startAgentName = startAgent
                .querySelector(".agent-card__name")
                .textContent
                .trim();
            
            editorState.allConfigsById[startAgentId]
                .agentConfiguration
                .children
                .push(endAgentName);

            editorState.allConfigsById[startAgentId]
                .agentConfiguration
                .childrenId
                .push(endAgentId);

            editorState.allConfigsById[endAgentId]
                .agentConfiguration
                .parents
                .push(startAgentName);

            editorState.allConfigsById[endAgentId]
                .agentConfiguration
                .parentsId
                .push(startAgentId);

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
        layout: {
            x: 0,
            y: 0
        },
        agentConfiguration: {
            agentId: agentId,
            agentInstructions: "",
            characterInput: false,
            scenario: false,
            carryOver: false,
            pastMessageCount: 0,
            parents: [],
            parentsId: [],
            children: [],
            childrenId: [],
            agentLLMConfig: {
                LLMName: "",
                temp: 1,
                maxTokens: 4000,
                topP: 1
            }
        }
    };
}

function syncAgentLayoutToEditorState() {
    document.querySelectorAll(".agent-card[data-agent-id]").forEach(function (agent) {
        const agentId = agent.dataset.agentId;

        if (!editorState.allConfigsById[agentId]) {
            editorState.allConfigsById[agentId] = createDefaultAgentConfig(agentId);
        }

        editorState.allConfigsById[agentId].layout = {
            x: Number.parseFloat(agent.style.left) || 0,
            y: Number.parseFloat(agent.style.top) || 0
        };
    });
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

        syncAgentLayoutToEditorState();

            const payload = Object.fromEntries(
                Object.entries(editorState.allConfigsById).map(([agentId, agentConfig]) => [
                    agentId,
                    {
                        ...agentConfig,
                        layout: {
                            ...agentConfig.layout
                        },
                        agentConfiguration: {
                            ...agentConfig.agentConfiguration,

                            parents: [...agentConfig.agentConfiguration.parents],
                            parentsId: [...agentConfig.agentConfiguration.parentsId],

                            children: [...agentConfig.agentConfiguration.children],
                            childrenId: [...agentConfig.agentConfiguration.childrenId],

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

async function openSavedLoadout(loadoutCardElement) {
    const loadoutId = loadoutCardElement.dataset.loadoutId;

    const response = await fetch(`/loadout-configuration/${loadoutId}`);

    if (!response.ok) {
        console.error("Failed to load loadout:", loadoutId);
        return;
    }

    const loadoutData = await response.json();

    showLoadoutEditor(loadoutCardElement);

    loadSavedLoadoutIntoEditor(loadoutData);
}

function loadSavedLoadoutIntoEditor(loadoutData) {
    const editor = document.querySelector(".loadout-editor");

    editorState.allConfigsById = {};
    editorState.allChildren = {};
    editorState.isDraggingAgent = false;
    editorState.isDraggingLine = false;
    editorState.draggedAgent = null;
    editorState.draggedLine = null;
    editorState.activeSvg = null;

    editor.querySelectorAll(".agent-card").forEach(function (agent) {
        agent.remove();
    });

    loadoutData.loadoutAgents.forEach(function (savedAgent) {
        const agent = createAgentCardFromSavedAgent(savedAgent);

        editor.appendChild(agent);

        editorState.allConfigsById[savedAgent.agentId] = {
            agentName: savedAgent.agentName,
            layout: savedAgent.layout || {
                x: 0,
                y: 0
            },
            agentConfiguration: {
                agentId: savedAgent.agentId,
                agentInstructions: savedAgent.agentInstructions || "",
                characterInput: savedAgent.characterInput || false,
                scenario: savedAgent.scenario || false,
                carryOver: savedAgent.carryOver || false,
                pastMessageCount: savedAgent.pastMessageCount || 0,

                parents: [],
                parentsId: savedAgent.parents || [],

                children: [],
                childrenId: savedAgent.children || [],

                agentLLMConfig: savedAgent.agentLLMConfig || {
                    LLMName: "",
                    temp: 1,
                    maxTokens: 4000,
                    topP: 1
                }
            }
        };

        editorState.allChildren[savedAgent.agentId] = new Set(savedAgent.children || []);

        registerAgent(agent);
    });

    requestAnimationFrame(function () {
        requestAnimationFrame(function () {
            rebuildAllSavedWires();
        });
    });
}

async function createAgentCardFromSavedAgent(savedAgent) {

    const agentWrapper = document.createElement("div");
    
    const response = await fetch("/render-agent-card", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            savedAgent: savedAgent,
        })
    });

    agentWrapper.innerHTML = await response.text().trim();
    
    const agent = agentWrapper.firstElementChild;

    const layout = savedAgent.layout || {
        x: 0,
        y: 0
    };

    agent.style.position = "absolute";
    agent.style.left = `${layout.x}px`;
    agent.style.top = `${layout.y}px`;

    return agent;
}

function rebuildAllSavedWires() {
    document.querySelectorAll(".wire-layer line").forEach(function (line) {
        line.remove();
    });

    Object.entries(editorState.allConfigsById).forEach(function ([startAgentId, agentConfigWrapper]) {
        const childrenIds = agentConfigWrapper.agentConfiguration.childrenId || [];

        childrenIds.forEach(function (endAgentId) {
            drawSavedWire(startAgentId, endAgentId);
        });
    });
}

function drawSavedWire(startAgentId, endAgentId) {
    const startAgent = document.querySelector(`.agent-card[data-agent-id="${startAgentId}"]`);
    const endAgent = document.querySelector(`.agent-card[data-agent-id="${endAgentId}"]`);

    if (!startAgent || !endAgent) return;

    const startOutput = startAgent.querySelector(".agent-port--out");
    const endInput = endAgent.querySelector(".agent-port--in");
    const svg = startAgent.querySelector(".wire-layer");

    if (!startOutput || !endInput || !svg) return;

    const svgRect = svg.getBoundingClientRect();
    const outRect = startOutput.getBoundingClientRect();
    const inRect = endInput.getBoundingClientRect();

    const startX = outRect.left + outRect.width / 2 - svgRect.left;
    const startY = outRect.top + outRect.height / 2 - svgRect.top;

    const endX = inRect.left + inRect.width / 2 - svgRect.left;
    const endY = inRect.top + inRect.height / 2 - svgRect.top;

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

    line.setAttribute("x1", startX);
    line.setAttribute("y1", startY);
    line.setAttribute("x2", endX);
    line.setAttribute("y2", endY);
    line.setAttribute("stroke", "white");
    line.setAttribute("stroke-width", "2");
    line.setAttribute("data-agent-start", startAgentId);
    line.setAttribute("data-agent-end", endAgentId);

    svg.appendChild(line);
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