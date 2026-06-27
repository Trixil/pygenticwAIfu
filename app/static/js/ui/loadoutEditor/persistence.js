(function () {
    const LoadoutEditor = window.LoadoutEditor;

    function serializeConfigsForSave() {
        return Object.fromEntries(
            Object.entries(LoadoutEditor.state.allConfigsById).map(function ([agentId, agentConfig]) {
                return [
                    agentId,
                    {
                        ...agentConfig,
                        layout: {
                            ...agentConfig.layout
                        },
                        agentConfiguration: {
                            ...agentConfig.agentConfiguration,
                            parents: [...(agentConfig.agentConfiguration.parents || [])],
                            children: [...(agentConfig.agentConfiguration.children || [])],
                            upperChildren: [...(agentConfig.agentConfiguration.upperChildren || [])],
                            lowerChildren: [...(agentConfig.agentConfiguration.lowerChildren || [])],
                            agentLLMConfig: {
                                ...agentConfig.agentConfiguration.agentLLMConfig
                            }
                        }
                    }
                ];
            })
        );
    }

    async function saveLoadoutConfiguration() {
        const loadoutEditor = LoadoutEditor.getLoadoutEditorElement();
        const loadoutId = loadoutEditor.dataset.loadoutId;
        const loadoutName = LoadoutEditor.getLoadoutTitleElement().innerText;

        LoadoutEditor.syncAgentLayoutToEditorState();

        const response = await fetch("/save-loadout-configuration", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                loadoutId: loadoutId,
                loadoutName: loadoutName,
                allConfigsById: serializeConfigsForSave()
            })
        });

        if (!response.ok) {
            console.error("Failed to save loadout configuration");
        }
    }
    
    function toggleDeleteLinks() {
        
        const isDeletingLinks = LoadoutEditor.state.isDeletingLinks;

        // #/#/ implement prettification
        
        LoadoutEditor.state.isDeletingLinks = !isDeletingLinks;

    }

    async function createAgentCardFromSavedAgent(savedAgent) {
        const runtimeAgent = LoadoutEditor.normalizeAgentConfig(savedAgent);
        const agentWrapper = document.createElement("div");
        const agentId = runtimeAgent.agentConfiguration.agentId;

        if (!LoadoutEditor.state.allConfigsById[agentId]) {
            LoadoutEditor.state.allConfigsById[agentId] = runtimeAgent;
        }

        const response = await fetch("/render-agent-card", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                agentConfig: runtimeAgent,
                agentName: runtimeAgent.agentName
            })
        });

        if (!response.ok) {
            console.error("Failed to render agent card");
            return null;
        }

        agentWrapper.innerHTML = (await response.text()).trim();
        const agent = agentWrapper.firstElementChild;
        const layout = runtimeAgent.layout || LoadoutEditor.defaultAgentPosition;

        agent.style.position = "absolute";
        agent.style.left = `${layout.x}px`;
        agent.style.top = `${layout.y}px`;

        return agent;
    }

    async function loadSavedLoadoutIntoEditor(loadoutData) {
        const title = LoadoutEditor.getLoadoutTitleElement();
        const editor = LoadoutEditor.getLoadoutEditorElement();

        title.textContent = loadoutData.loadoutName;

        LoadoutEditor.resetEditorState();
        LoadoutEditor.clearEditorSurface(editor);

        for (const savedAgent of loadoutData.loadoutAgents) {
            const runtimeAgent = LoadoutEditor.normalizeAgentConfig(savedAgent);
            const agentId = runtimeAgent.agentConfiguration.agentId;

            LoadoutEditor.state.allConfigsById[agentId] = runtimeAgent;
            LoadoutEditor.state.allChildren[agentId] = new Set(
                runtimeAgent.agentConfiguration.children || []
            );

            const agent = await createAgentCardFromSavedAgent(runtimeAgent);
            if (!agent) continue;

            editor.appendChild(agent);
            LoadoutEditor.registerAgent(agent);
        }

        LoadoutEditor.startLoadoutEditor();

        requestAnimationFrame(function () {
            LoadoutEditor.rebuildAllSavedWires();
        });
    }

    async function openSavedLoadout(loadoutCardElement) {
        if (loadoutCardElement.classList.contains("selectable-for-chat")) {
            loadoutCardElement.classList.toggle("selected-for-chat");
            return;
        }

        const loadoutId = loadoutCardElement.dataset.loadoutId;
        const response = await fetch(`/loadout-configuration/${loadoutId}`);

        if (!response.ok) {
            console.error("Failed to load loadout:", loadoutId);
            return;
        }

        const loadoutData = await response.json();
        LoadoutEditor.showLoadoutEditor(loadoutCardElement);
        await loadSavedLoadoutIntoEditor(loadoutData);
    }

    async function addNewAgent() {
        const agentId = LoadoutEditor.generateId();
        const runtimeAgent = LoadoutEditor.createDefaultAgentConfig(agentId);
        const editor = LoadoutEditor.getLoadoutEditorElement();

        LoadoutEditor.state.allConfigsById[agentId] = runtimeAgent;
        LoadoutEditor.state.allChildren[agentId] = new Set();

        const newAgent = await createAgentCardFromSavedAgent(runtimeAgent);
        if (!newAgent) return;

        editor.appendChild(newAgent);
        LoadoutEditor.registerAgent(newAgent);
    }

    Object.assign(LoadoutEditor, {
        addNewAgent,
        createAgentCardFromSavedAgent,
        loadSavedLoadoutIntoEditor,
        openSavedLoadout,
        saveLoadoutConfiguration,
        toggleDeleteLinks
    });
})();
