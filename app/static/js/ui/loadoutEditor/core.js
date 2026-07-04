(function () {
    const LoadoutEditor = window.LoadoutEditor || (window.LoadoutEditor = {});

    const defaultAgentPosition = { x: 100, y: 100 };
    const editorState = LoadoutEditor.state || {
        allConfigsById: {},
        allChildren: {},
        allUpperChildren: {},
        allLowerChildren: {},
        isDraggingAgent: false,
        isDraggingLine: false,
        draggedAgent: null,
        draggedLine: null,
        activeSvg: null,
        xOffset: 0,
        yOffset: 0,
        hasEditorDragListeners: false,
        hasSaveListener: false,
        hasDeletingLinksListener: false,
        hasTitleListeners: false,
        isDeletingLinks: false
    };

    function getLayoutElement() {
        return document.querySelector(".layout");
    }

    function getCharacterCardsElement() {
        return document.querySelector("#character-cards");
    }

    function getLoadoutCardsElement() {
        return document.querySelector("#loadout-cards");
    }

    function getLoadoutEditorElement() {
        return document.querySelector(".loadout-editor");
    }

    function getLoadoutTitleElement() {
        return document.querySelector(".loadout-config-header");
    }

    function getAgentElement(agentId) {
        return document.querySelector(`.loadout-editor .agent-card[data-agent-id="${agentId}"]`);
    }

    function getPaneForAgent(agentId) {
        return document.querySelector(
            `.loadout-editor-pane[data-selected-agent-id="${agentId}"]`
        );
    }

    function getEditorAgents() {
        return [...document.querySelectorAll(".loadout-editor .agent-card[data-agent-id]")];
    }

    function setButtonChecked(button, isChecked) {
        if (!button) return;
        button.classList.toggle("agent-card__button--checked", Boolean(isChecked));
    }

    function generateId() {
        return crypto.randomUUID().replace(/-/g, "");
    }

    function createDefaultAgentConfig(agentId) {
        return {
            agentName: "Untitled agent",
            layout: {
                x: defaultAgentPosition.x,
                y: defaultAgentPosition.y
            },
            agentConfiguration: {
                agentId: agentId,
                agentInstructions:
                    "Why do they call it the oven when you of in the cold food of out hot eat the food?",
                characterInput: false,
                scenario: false,
                carryOver: false,
                carryOverAgentId: "",
                carryOverAgentName: "",
                agentBranch: false,
                agentBranchUpperTrigger: "",
                agentBranchUpperInstructions: "",
                agentBranchLowerTrigger: "",
                agentBranchLowerInstructions: "",
                softActivation: true,
                maxLoop: 2,
                publish: false,
                writeLorebook: false,
                queryLorebook: false,
                pastMessageCount: 0,
                parents: [],
                children: [],
                upperChildren: [],
                lowerChildren: [],
                agentLLMConfig: {
                    LLMName: "openai/gpt-4.1",
                    temp: 1,
                    maxTokens: 4000,
                    topP: 1
                }
            }
        };
    }

    function normalizeAgentConfig(agentData) {
        const sourceConfig = agentData.agentConfiguration || agentData;
        const agentId = sourceConfig.agentId || agentData.agentId || generateId();
        const normalized = createDefaultAgentConfig(agentId);

        normalized.agentName = agentData.agentName || normalized.agentName;

        const layout = agentData.layout || normalized.layout;
        normalized.layout = {
            x: Number.parseFloat(layout.x) || defaultAgentPosition.x,
            y: Number.parseFloat(layout.y) || defaultAgentPosition.y
        };

        normalized.agentConfiguration = {
            ...normalized.agentConfiguration,
            agentInstructions:
                sourceConfig.agentInstructions ?? normalized.agentConfiguration.agentInstructions,
            characterInput: Boolean(sourceConfig.characterInput),
            scenario: Boolean(sourceConfig.scenario),
            carryOver: Boolean(sourceConfig.carryOver),
            carryOverAgentId: sourceConfig.carryOverAgentId || "",
            carryOverAgentName: sourceConfig.carryOverAgentName || "",
            agentBranch: sourceConfig.agentBranch,
            agentBranchUpperTrigger: sourceConfig.agentBranchUpperTrigger,
            agentBranchUpperInstructions: sourceConfig.agentBranchUpperInstructions,
            agentBranchLowerTrigger: sourceConfig.agentBranchLowerTrigger,
            agentBranchLowerInstructions: sourceConfig.agentBranchLowerInstructions,
            pastMessageCount: normalizePastMessageCount(sourceConfig.pastMessageCount),
            publish: Boolean(sourceConfig.publish),
            softActivation: Boolean(sourceConfig.softActivation),
            parents: [...(sourceConfig.parents || [])],
            children: [...(sourceConfig.children || [])],
            upperChildren: [...(sourceConfig.upperChildren || [])],
            lowerChildren: [...(sourceConfig.lowerChildren || [])],
            agentLLMConfig: {
                ...normalized.agentConfiguration.agentLLMConfig,
                ...(sourceConfig.agentLLMConfig || {})
            }
        };

        return normalized;
    }

    function ensureAgentConfig(agentId) {
        if (!editorState.allConfigsById[agentId]) {
            editorState.allConfigsById[agentId] = createDefaultAgentConfig(agentId);
        }

        return editorState.allConfigsById[agentId];
    }

    function ensureChildrenSet(agentId) {
        if (!editorState.allChildren[agentId] || !ensureAgentConfig(agentId).agentBranch)  {
            const config = ensureAgentConfig(agentId);
            editorState.allChildren[agentId] = new Set(config.agentConfiguration.children || []);
        }
        
        return editorState.allChildren[agentId];
    }

    function ensureBranchChildrenSet(agentId) {
        const config = ensureAgentConfig(agentId);

        if (!editorState.allUpperChildren[agentId]) {
            editorState.allUpperChildren[agentId] = new Set(
                config.agentConfiguration.upperChildren || []
            );
        }

        if (!editorState.allLowerChildren[agentId]) {
            editorState.allLowerChildren[agentId] = new Set(
                config.agentConfiguration.lowerChildren || []
            );
        }

        return {
            upperChildren: editorState.allUpperChildren[agentId],
            lowerChildren: editorState.allLowerChildren[agentId]
        };
    }

    function normalizePastMessageCount(value) {
        const number = Number(value);

        if (!Number.isFinite(number) || number < 0) {
            return 0;
        }

        return Math.floor(number);
    }

    function setPastMessageCount(agentId, value) {
        const count = normalizePastMessageCount(value);
        const config = ensureAgentConfig(agentId).agentConfiguration;

        config.pastMessageCount = count;

        const agent = getAgentElement(agentId);
        const pane = getPaneForAgent(agentId);

        const cardInput = agent?.querySelector(".agent-card__chat-count-input");
        const paneInput = pane?.querySelector("#loadout-past-messages");

        if (cardInput) {
            cardInput.value = count;
        }

        if (paneInput) {
            paneInput.value = count;
        }

        return count;
    }

    function setAgentToggle(agentId, configKey, isChecked) {
        const checked = Boolean(isChecked);
        const config = ensureAgentConfig(agentId).agentConfiguration;
        const agent = getAgentElement(agentId);
        const pane = getPaneForAgent(agentId);

        config[configKey] = checked;

        if (configKey === "characterInput") {
            setButtonChecked(agent?.querySelector(".agent-character-input"), checked);
            const checkbox = pane?.querySelector("#loadout-use-character-cards");
            if (checkbox) checkbox.checked = checked;
        }

        if (configKey === "scenario") {
            setButtonChecked(agent?.querySelector(".agent-scenario"), checked);
            const checkbox = pane?.querySelector("#loadout-use-scenario");
            if (checkbox) checkbox.checked = checked;
        }

        if (configKey === "carryOver") {
            setButtonChecked(agent?.querySelector(".agent-carryover"), checked);
            const checkbox = pane?.querySelector("#loadout-use-carryover");
            const input = pane?.querySelector("#loadout-carryover-agent-name");

            if (checkbox) checkbox.checked = checked;
            if (input) input.disabled = !checked;
        }

        return checked;
    }

    function setCarryOverAgent(agentId, carryOverAgentId, carryOverAgentName) {
        const config = ensureAgentConfig(agentId).agentConfiguration;
        const pane = getPaneForAgent(agentId);

        config.carryOverAgentId = carryOverAgentId || "";
        config.carryOverAgentName = carryOverAgentName || "";

        const input = pane?.querySelector("#loadout-carryover-agent-name");
        if (input) {
            input.value = config.carryOverAgentName;
        }
    }

    function refreshPublish(agentId) {
        const publishIcon = LoadoutEditor
        .getAgentElement(agentId)
        .querySelector(".agent-card__publish-icon");
        
        const config = LoadoutEditor.ensureAgentConfig(agentId).agentConfiguration;
        const hasChildren =
        (config.upperChildren.length ||
            config.lowerChildren.length ||
            config.children.length);
        
        if (!hasChildren) {
            const allAgentIds = Object.keys(editorState.allConfigsById);
            
            const previousPublishId = allAgentIds.find((thisAgentId) => {
                const isThisPublish = LoadoutEditor.ensureAgentConfig(thisAgentId).agentConfiguration.publish;
                return isThisPublish;
            });

            if (previousPublishId) {
                LoadoutEditor.setPublish(previousPublishId, false);
            }
            LoadoutEditor.setPublish(agentId, true);
        }
    }

    function setPublish(agentId, isPublish) {
        const publishIcon = LoadoutEditor
        .getAgentElement(agentId)
        .querySelector(".agent-card__publish-icon");
        
        const config = LoadoutEditor.ensureAgentConfig(agentId).agentConfiguration;
        const hasChildren =
        (config.upperChildren.length ||
            config.lowerChildren.length ||
            config.children.length);
            
        publishIcon.classList.toggle("hidden", hasChildren);
        publishIcon.classList.toggle("enabled", isPublish);
        publishIcon.classList.toggle("disabled", !isPublish);
        
        const allAgentIds = Object.keys(editorState.allConfigsById);

        const previousPublishId = allAgentIds.find((thisAgentId) => {
            const isThisPublish = LoadoutEditor.ensureAgentConfig(thisAgentId).agentConfiguration.publish;
            return isThisPublish;
        })
        if (isPublish) {

            if (previousPublishId) {
                const publishIcon = LoadoutEditor
                    .getAgentElement(previousPublishId)
                    .querySelector(".agent-card__publish-icon");
                
                const previousConfig = LoadoutEditor.ensureAgentConfig(previousPublishId).agentConfiguration;
                const previousHasChildren =
                (previousConfig.upperChildren.length ||
                    previousConfig.lowerChildren.length ||
                    previousConfig.children.length);
                    
                publishIcon.classList.toggle("hidden", previousHasChildren);
                publishIcon.classList.toggle("enabled", false);
                publishIcon.classList.toggle("disabled", true);
                previousConfig.publish = false;
            }
        }
        else if (previousPublishId === agentId) {
            const childlessId = allAgentIds.find((thisAgentId) => {
                const thisConfig = LoadoutEditor.ensureAgentConfig(thisAgentId).agentConfiguration;
                
                return (
                    thisConfig.children.length === 0 &&
                    thisConfig.upperChildren.length === 0 &&
                    thisConfig.lowerChildren.length === 0 &&
                    thisAgentId !== agentId
                );
            })
            
            if (childlessId) {
                setPublish(childlessId, true);
            }
            else {
                throw new Error("Can't find childless agent to set as the publisher");
            }
        }
        config.publish = isPublish;

    }

    function autoGrowTextarea(textarea) {
        const scrollParent = textarea.closest(".loadout-editor-pane--body");
        const oldScrollTop = scrollParent ? scrollParent.scrollTop : 0;

        textarea.style.height = "auto";
        textarea.style.height = `${textarea.scrollHeight}px`;

        if (scrollParent) {
            scrollParent.scrollTop = oldScrollTop;
        }
    }

    function syncAgentLayoutToEditorState() {
        getEditorAgents().forEach(function (agent) {
            const agentId = agent.dataset.agentId;
            const config = ensureAgentConfig(agentId);

            config.layout = {
                x: Number.parseFloat(agent.style.left) || 0,
                y: Number.parseFloat(agent.style.top) || 0
            };
        });
    }

    function resetEditorState() {
        editorState.allConfigsById = {};
        editorState.allChildren = {};
        editorState.isDraggingAgent = false;
        editorState.isDraggingLine = false;
        editorState.draggedAgent = null;
        editorState.draggedLine = null;
        editorState.activeSvg = null;
        editorState.xOffset = 0;
        editorState.yOffset = 0;
        editorState.isDeletingLinks = false;
    }

    function clearEditorSurface(editor) {
        const targetEditor = editor || getLoadoutEditorElement();
        if (!targetEditor) return;

        targetEditor
            .querySelectorAll(".agent-card, .loadout-editor-pane")
            .forEach(function (element) {
                element.remove();
            });
    }

    function showLoadoutEditor(loadoutCardElement) {
        const layout = getLayoutElement();
        const characterCards = getCharacterCardsElement();
        const loadoutCards = getLoadoutCardsElement();
        const editor = getLoadoutEditorElement();
        const title = getLoadoutTitleElement();

        if (!layout || !characterCards || !loadoutCards || !editor) return;

        layout.classList.add("config-expand-hide");
        layout.classList.add("config-expand-widen");

        characterCards.classList.add("hidden");
        loadoutCards.classList.add("hidden");
        editor.classList.remove("hidden");

        let loadoutId = loadoutCardElement.dataset.loadoutId;

        if (loadoutId === "NEW LOADOUT") {
            loadoutId = generateId();
            resetEditorState();
            clearEditorSurface(editor);

            if (title) {
                title.textContent = "Untitled Loadout Configuration";
            }
        }

        editor.setAttribute("data-loadout-id", loadoutId);
    }

    Object.assign(LoadoutEditor, {
        autoGrowTextarea,
        clearEditorSurface,
        createDefaultAgentConfig,
        defaultAgentPosition,
        ensureAgentConfig,
        ensureChildrenSet,
        ensureBranchChildrenSet,
        generateId,
        getAgentElement,
        getCharacterCardsElement,
        getEditorAgents,
        getLayoutElement,
        getLoadoutCardsElement,
        getLoadoutEditorElement,
        getLoadoutTitleElement,
        getPaneForAgent,
        normalizeAgentConfig,
        normalizePastMessageCount,
        resetEditorState,
        setPublish,
        refreshPublish,
        setAgentToggle,
        setButtonChecked,
        setCarryOverAgent,
        setPastMessageCount,
        showLoadoutEditor,
        state: editorState,
        syncAgentLayoutToEditorState
    });
})();
