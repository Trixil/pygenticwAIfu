(function () {
    const LoadoutEditor = window.LoadoutEditor;

    function hideEditorPane(editorPane) {
        editorPane.classList.add("pane-hidden");

        editorPane.addEventListener(
            "transitionend",
            function handleTransitionEnd(event) {
                if (event.propertyName !== "transform") return;
                editorPane.remove();
            },
            { once: true }
        );
    }

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
            const config = LoadoutEditor.ensureAgentConfig(agentId);
            nameInput.value = config.agentName || overviewName.textContent.trim();
            nameInput.readOnly = true;
        }

        function commitNameChange() {
            const configWrapper = LoadoutEditor.ensureAgentConfig(agentId);
            const config = configWrapper.agentConfiguration;
            const oldName = configWrapper.agentName || overviewName.textContent.trim();
            const newName = nameInput.value.trim().replace(/\s{2,}/g, " ");

            if (newName === "") {
                resetNameInput();
                return;
            }

            const duplicateNameExists = Object.entries(LoadoutEditor.state.allConfigsById).some(
                function ([otherAgentId, otherConfig]) {
                    return otherAgentId !== agentId && otherConfig.agentName === newName;
                }
            );

            if (duplicateNameExists) {
                showToast("Two agents can't have the same name! Get creative, BAKA~!");
                resetNameInput();
                return;
            }

            configWrapper.agentName = newName;

            if (!config.carryOverAgentName || config.carryOverAgentName === oldName) {
                config.carryOverAgentName = newName;
                const carryoverInput = editorPane.querySelector("#loadout-carryover-agent-name");

                if (carryoverInput) {
                    carryoverInput.value = newName;
                }
            }

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
                resetNameInput();
                nameInput.blur();
            }
        });
    }

    function registerLoadoutPaneControls(editorPane, agentId, agent) {
        const agentConfig = LoadoutEditor.ensureAgentConfig(agentId);
        const config = agentConfig.agentConfiguration;

        const hideButton = editorPane.querySelector(".loadout-editor-pane-hide-button");
        hideButton.addEventListener("click", function (event) {
            event.stopPropagation();
            hideEditorPane(editorPane);
        });

        editorPane.querySelectorAll(".loadout-editor-pane--tab").forEach(function (tab) {
            tab.addEventListener("click", function () {
                editorPane.dataset.activeTab = tab.dataset.tab;
            });
        });

        const instructionsTextarea = editorPane.querySelector(
            ".loadout-editor-instructions-textarea"
        );
        instructionsTextarea.addEventListener("input", function () {
            const instructions = instructionsTextarea.value;

            config.agentInstructions = instructions;

            agent.querySelector(".agent-card__instructions").textContent =
                instructions.slice(0, 250);
            agent.querySelector(".token-bubble .agent-card__meta-text").textContent =
                `~${Math.ceil(instructions.length / 4)} tokens`;

            LoadoutEditor.autoGrowTextarea(instructionsTextarea);
        });
        LoadoutEditor.autoGrowTextarea(instructionsTextarea);

        const modelNameInput = editorPane.querySelector("#loadout-model-name");
        const temperatureInput = editorPane.querySelector("#loadout-temperature");
        const topPInput = editorPane.querySelector("#loadout-top-p");
        const maxTokensInput = editorPane.querySelector("#loadout-max-tokens");

        modelNameInput.addEventListener("input", function () {
            config.agentLLMConfig.LLMName = modelNameInput.value;
            agent.querySelector(".model-bubble .agent-card__meta-text").textContent =
                modelNameInput.value;
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

        const pastMessagesInput = editorPane.querySelector("#loadout-past-messages");
        LoadoutEditor.setPastMessageCount(agentId, config.pastMessageCount);
        pastMessagesInput.addEventListener("input", function () {
            LoadoutEditor.setPastMessageCount(agentId, pastMessagesInput.value);
        });

        const characterCardsCheckbox = editorPane.querySelector("#loadout-use-character-cards");
        const scenarioCheckbox = editorPane.querySelector("#loadout-use-scenario");
        const carryOverCheckbox = editorPane.querySelector("#loadout-use-carryover");
        const carryoverAgentInput = editorPane.querySelector("#loadout-carryover-agent-name");

        characterCardsCheckbox.addEventListener("change", function () {
            LoadoutEditor.setAgentToggle(agentId, "characterInput", characterCardsCheckbox.checked);
        });

        scenarioCheckbox.addEventListener("change", function () {
            LoadoutEditor.setAgentToggle(agentId, "scenario", scenarioCheckbox.checked);
        });

        carryOverCheckbox.addEventListener("change", function () {
            LoadoutEditor.setAgentToggle(agentId, "carryOver", carryOverCheckbox.checked);
        });

        carryoverAgentInput.disabled = !carryOverCheckbox.checked;

        carryoverAgentInput.addEventListener("input", function () {
            config.carryOverAgentName = carryoverAgentInput.value.trim();
        });

        function validateCarryoverAgentName() {
            const carryoverAgentName = carryoverAgentInput.value.trim();

            if (!carryOverCheckbox.checked) {
                return true;
            }

            const matchingConfig = Object.values(LoadoutEditor.state.allConfigsById).find(
                function (thisConfig) {
                    return thisConfig.agentName === carryoverAgentName;
                }
            );

            if (!matchingConfig) {
                showToast("Agent name not found.");
                return false;
            }

            LoadoutEditor.setCarryOverAgent(
                agentId,
                matchingConfig.agentConfiguration.agentId,
                matchingConfig.agentName
            );

            return true;
        }

        carryoverAgentInput.addEventListener("blur", validateCarryoverAgentName);

        const branchAgentCheckbox = editorPane.querySelector("#loadout-use-branch");
        const agentBranchUpperTrigger = editorPane.querySelector("#loadout-upper-branch-trigger");
        const agentBranchUpperInstructions = editorPane.querySelector("#loadout-upper-branch-instructions");
        const agentBranchLowerTrigger = editorPane.querySelector("#loadout-lower-branch-trigger");
        const agentBranchLowerInstructions = editorPane.querySelector("#loadout-lower-branch-instructions");

        branchAgentCheckbox.addEventListener("change", function () {
            const useBranch = branchAgentCheckbox.checked;
            LoadoutEditor.setAgentToggle(agentId, "branchAgent", branchAgentCheckbox.checked);
            agentBranchUpperTrigger.closest(".loadout-editor-section")
            .classList.toggle("hidden", !useBranch);
            agentBranchUpperInstructions.closest(".loadout-editor-section")
            .classList.toggle("hidden", !useBranch);
            agentBranchLowerTrigger.closest(".loadout-editor-section")
            .classList.toggle("hidden", !useBranch);
            agentBranchLowerInstructions.closest(".loadout-editor-section")
            .classList.toggle("hidden", !useBranch);

            agent.querySelector(".agent-port--out-upper").classList.toggle("hidden", !useBranch)
            agent.querySelector(".agent-port--out-lower").classList.toggle("hidden", !useBranch)
            agent.querySelector(".agent-port--out").classList.toggle("hidden", useBranch)

            config.agentBranch = useBranch;
        });

        agentBranchUpperTrigger.addEventListener("input", function () {
            config.agentBranchUpperTrigger = agentBranchUpperTrigger.value.trim();
        });
        agentBranchUpperInstructions.addEventListener("input", function () {
            config.agentBranchUpperInstructions = agentBranchUpperInstructions.value.trim();
        });
        agentBranchLowerTrigger.addEventListener("input", function () {
            config.agentBranchLowerTrigger = agentBranchLowerTrigger.value.trim();
        });
        agentBranchLowerInstructions.addEventListener("input", function () {
            config.agentBranchLowerInstructions = agentBranchLowerInstructions.value.trim();
        });
        
        registerPaneNameEditor(editorPane, agentId, agent);
    }

    async function showAgentPane(agent) {
        const agentId = agent.dataset.agentId;
        const agentName = agent.querySelector(".agent-card__name").textContent.trim();
        const agentConfig = LoadoutEditor.ensureAgentConfig(agentId);
        const loadoutId = LoadoutEditor.getLoadoutEditorElement()?.dataset.loadoutId;

        const agentNamesById = {};
        LoadoutEditor.getEditorAgents().forEach(function (editorAgent) {
            agentNamesById[editorAgent.dataset.agentId] =
                editorAgent.querySelector(".agent-card__name").textContent.trim();
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

        const existingPane = LoadoutEditor.getPaneForAgent(agentId);
        if (existingPane) {
            existingPane.remove();
        }

        const wrapper = document.createElement("div");
        wrapper.innerHTML = (await response.text()).trim();

        const editorPane = wrapper.firstElementChild;
        editorPane.dataset.selectedAgentId = agentId;
        editorPane.classList.add("pane-hidden");

        LoadoutEditor.getLoadoutEditorElement().appendChild(editorPane);
        registerLoadoutPaneControls(editorPane, agentId, agent);

        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                editorPane.classList.remove("pane-hidden");
            });
        });
    }

    Object.assign(LoadoutEditor, {
        registerLoadoutPaneControls,
        showAgentPane
    });
})();
