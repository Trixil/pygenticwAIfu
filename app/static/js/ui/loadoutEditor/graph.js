(function () {
    const LoadoutEditor = window.LoadoutEditor;

    function getCenterInSvg(element, svg) {
        const rect = element.getBoundingClientRect();
        const svgRect = svg.getBoundingClientRect();

        return {
            x: rect.left + rect.width / 2 - svgRect.left,
            y: rect.top + rect.height / 2 - svgRect.top
        };
    }

    function updateConnectedLines(agent, svg) {
        const agentId = agent.dataset.agentId;

        svg.querySelectorAll(
            `line[data-agent-start="${agentId}"], line[data-agent-end="${agentId}"]`
        ).forEach(function (line) {
            const startAgent = document.querySelector(
                `.agent-card[data-agent-id="${line.dataset.agentStart}"]`
            );
            const endAgent = document.querySelector(
                `.agent-card[data-agent-id="${line.dataset.agentEnd}"]`
            );
            const startOutput = startAgent?.querySelector(".agent-port--out");
            const endInput = endAgent?.querySelector(".agent-port--in");

            if (startOutput) {
                const start = getCenterInSvg(startOutput, svg);
                line.setAttribute("x1", start.x);
                line.setAttribute("y1", start.y);
            }

            if (endInput) {
                const end = getCenterInSvg(endInput, svg);
                line.setAttribute("x2", end.x);
                line.setAttribute("y2", end.y);
            }
        });
    }

    function resetLineDrag() {
        const state = LoadoutEditor.state;

        if (state.draggedLine) {
            state.draggedLine.remove();
        }

        state.isDraggingLine = false;
        state.draggedLine = null;
        state.activeSvg = null;
    }

    function isLoop(source, destination, kindergarten) {
        const destinationChildren = [...(kindergarten[destination] ?? [])];

        if (destinationChildren.includes(source)) {
            return true;
        }

        return destinationChildren.some(function (child) {
            return isLoop(source, child, kindergarten);
        });
    }

    function registerAgent(agent) {
        const state = LoadoutEditor.state;
        const agentId = agent.dataset.agentId;

        if (agent.dataset.registered === "true") return;
        agent.dataset.registered = "true";

        const agentConfig = LoadoutEditor.ensureAgentConfig(agentId);
        const config = agentConfig.agentConfiguration;
        LoadoutEditor.ensureChildrenSet(agentId);

        if (!config.carryOverAgentName) {
            config.carryOverAgentName = agentConfig.agentName;
        }

        const agentOutput = agent.querySelector(".agent-port--out");
        const agentInput = agent.querySelector(".agent-port--in");
        const svgLayer = agent.querySelector(".wire-layer");
        const carryOverButton = agent.querySelector(".agent-carryover");
        const scenarioButton = agent.querySelector(".agent-scenario");
        const characterInputButton = agent.querySelector(".agent-character-input");
        const agentNameElement = agent.querySelector(".agent-card__name");
        const agentPastMessagesInput = agent.querySelector(".agent-card__chat-count-input");

        [carryOverButton, scenarioButton, characterInputButton, agentPastMessagesInput].forEach(
            function (element) {
                element?.addEventListener("pointerdown", function (event) {
                    event.stopPropagation();
                });
            }
        );

        carryOverButton.addEventListener("click", function (event) {
            event.stopPropagation();
            const nextChecked = !carryOverButton.classList.contains("agent-card__button--checked");
            LoadoutEditor.setAgentToggle(agentId, "carryOver", nextChecked);
        });

        scenarioButton.addEventListener("click", function (event) {
            event.stopPropagation();
            const nextChecked = !scenarioButton.classList.contains("agent-card__button--checked");
            LoadoutEditor.setAgentToggle(agentId, "scenario", nextChecked);
        });

        characterInputButton.addEventListener("click", function (event) {
            event.stopPropagation();
            const nextChecked =
                !characterInputButton.classList.contains("agent-card__button--checked");
            LoadoutEditor.setAgentToggle(agentId, "characterInput", nextChecked);
        });

        agentPastMessagesInput.addEventListener("input", function () {
            LoadoutEditor.setPastMessageCount(agentId, agentPastMessagesInput.value);
        });

        agent.addEventListener("pointerup", function (upEvent) {
            if (!state.isDraggingAgent || state.draggedAgent !== agent) return;

            state.isDraggingAgent = false;
            state.draggedAgent = null;
            agent.releasePointerCapture(upEvent.pointerId);
        });

        agent.addEventListener("pointerdown", function (downEvent) {
            const outRect = agentOutput.getBoundingClientRect();
            const clickedOutput =
                downEvent.clientX >= outRect.left &&
                downEvent.clientX <= outRect.right &&
                downEvent.clientY >= outRect.top &&
                downEvent.clientY <= outRect.bottom;

            if (clickedOutput) return;

            state.isDraggingAgent = true;
            state.draggedAgent = agent;

            const rect = agent.getBoundingClientRect();
            state.xOffset = downEvent.clientX - rect.left;
            state.yOffset = downEvent.clientY - rect.top;

            agent.setPointerCapture(downEvent.pointerId);
        });

        [agentNameElement, agent.querySelector(".agent-instructions")].forEach(function (element) {
            if (!element) return;

            element.addEventListener("pointerdown", function (event) {
                event.stopPropagation();
            });

            element.addEventListener("pointerup", function (event) {
                event.stopPropagation();
            });

            element.addEventListener("click", function (event) {
                event.stopPropagation();
                LoadoutEditor.showAgentPane(agent);
            });
        });

        agentOutput.addEventListener("pointerdown", function (downEvent) {
            downEvent.stopPropagation();

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            const svgRect = svgLayer.getBoundingClientRect();
            const outRect = agentOutput.getBoundingClientRect();

            state.draggedLine = line;
            state.activeSvg = svgLayer;
            state.isDraggingLine = true;

            line.setAttribute("x1", outRect.left + outRect.width / 2 - svgRect.left);
            line.setAttribute("y1", outRect.top + outRect.height / 2 - svgRect.top);
            line.setAttribute("x2", downEvent.clientX - svgRect.left);
            line.setAttribute("y2", downEvent.clientY - svgRect.top);
            line.setAttribute("stroke", "white");
            line.setAttribute("stroke-width", "2");
            line.setAttribute("data-agent-start", agentId);

            svgLayer.appendChild(line);
        });

        agentInput.addEventListener("pointerup", function () {
            if (!state.isDraggingLine || !state.draggedLine || !state.activeSvg) {
                return;
            }

            const startAgentId = state.draggedLine.getAttribute("data-agent-start");
            const endAgentId = agentId;

            if (
                startAgentId === endAgentId ||
                isLoop(startAgentId, endAgentId, state.allChildren) ||
                LoadoutEditor.ensureChildrenSet(startAgentId).has(endAgentId)
            ) {
                resetLineDrag();
                return;
            }

            const svgRect = state.activeSvg.getBoundingClientRect();
            const inRect = agentInput.getBoundingClientRect();
            const startX = Number(state.draggedLine.getAttribute("x1"));
            const startY = Number(state.draggedLine.getAttribute("y1"));
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

            state.activeSvg.appendChild(connectorLine);

            LoadoutEditor.ensureChildrenSet(startAgentId).add(endAgentId);

            const startChildren =
                LoadoutEditor.ensureAgentConfig(startAgentId).agentConfiguration.children;
            const endParents = LoadoutEditor.ensureAgentConfig(endAgentId).agentConfiguration.parents;

            if (!startChildren.includes(endAgentId)) {
                startChildren.push(endAgentId);
            }

            if (!endParents.includes(startAgentId)) {
                endParents.push(startAgentId);
            }

            resetLineDrag();
        });
    }

    function registerAllAgents() {
        LoadoutEditor.getEditorAgents().forEach(registerAgent);
    }

    function attachEditorDragListeners() {
        const state = LoadoutEditor.state;
        if (state.hasEditorDragListeners) return;

        document.addEventListener("pointermove", function (moveEvent) {
            if (!state.isDraggingAgent && !state.isDraggingLine) return;

            if (state.isDraggingAgent && state.draggedAgent) {
                const draggedAgent = state.draggedAgent;
                const parentRect = draggedAgent.offsetParent.getBoundingClientRect();

                draggedAgent.style.left =
                    `${moveEvent.clientX - parentRect.left - state.xOffset}px`;
                draggedAgent.style.top =
                    `${moveEvent.clientY - parentRect.top - state.yOffset}px`;

                const draggedSvgLayer = draggedAgent.querySelector(".wire-layer");
                updateConnectedLines(draggedAgent, draggedSvgLayer);

                const draggedAgentId = draggedAgent.dataset.agentId;
                const draggedAgentConfig = LoadoutEditor.ensureAgentConfig(draggedAgentId);
                const draggedAgentParents =
                    draggedAgentConfig.agentConfiguration.parents || [];

                draggedAgentParents.forEach(function (parentAgentId) {
                    const parentAgentElement = LoadoutEditor.getAgentElement(parentAgentId);
                    const parentSvgLayer = parentAgentElement?.querySelector(".wire-layer");

                    if (parentAgentElement && parentSvgLayer) {
                        updateConnectedLines(parentAgentElement, parentSvgLayer);
                    }
                });
            }

            if (state.isDraggingLine && state.draggedLine && state.activeSvg) {
                const svgRect = state.activeSvg.getBoundingClientRect();

                state.draggedLine.setAttribute("x2", moveEvent.clientX - svgRect.left);
                state.draggedLine.setAttribute("y2", moveEvent.clientY - svgRect.top);
            }
        });

        document.addEventListener("pointerup", function () {
            if (state.draggedLine) {
                state.draggedLine.remove();
            }

            state.isDraggingAgent = false;
            state.draggedAgent = null;
            state.isDraggingLine = false;
            state.draggedLine = null;
            state.activeSvg = null;
        });

        state.hasEditorDragListeners = true;
    }

    function drawSavedWire(startAgentId, endAgentId) {
        const startAgent = LoadoutEditor.getAgentElement(startAgentId);
        const endAgent = LoadoutEditor.getAgentElement(endAgentId);

        if (!startAgent || !endAgent) return;

        const startOutput = startAgent.querySelector(".agent-port--out");
        const endInput = endAgent.querySelector(".agent-port--in");
        const svg = startAgent.querySelector(".wire-layer");

        if (!startOutput || !endInput || !svg) return;

        const svgRect = svg.getBoundingClientRect();
        const outRect = startOutput.getBoundingClientRect();
        const inRect = endInput.getBoundingClientRect();

        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", outRect.left + outRect.width / 2 - svgRect.left);
        line.setAttribute("y1", outRect.top + outRect.height / 2 - svgRect.top);
        line.setAttribute("x2", inRect.left + inRect.width / 2 - svgRect.left);
        line.setAttribute("y2", inRect.top + inRect.height / 2 - svgRect.top);
        line.setAttribute("stroke", "white");
        line.setAttribute("stroke-width", "2");
        line.setAttribute("data-agent-start", startAgentId);
        line.setAttribute("data-agent-end", endAgentId);

        svg.appendChild(line);
    }

    function rebuildAllSavedWires() {
        document.querySelectorAll(".loadout-editor .wire-layer line").forEach(function (line) {
            line.remove();
        });

        Object.entries(LoadoutEditor.state.allConfigsById).forEach(function (
            [startAgentId, agentConfigWrapper]
        ) {
            const childIds = agentConfigWrapper.agentConfiguration.children || [];

            childIds.forEach(function (endAgentId) {
                drawSavedWire(startAgentId, endAgentId);
            });
        });
    }

    Object.assign(LoadoutEditor, {
        attachEditorDragListeners,
        drawSavedWire,
        isLoop,
        rebuildAllSavedWires,
        registerAgent,
        registerAllAgents,
        updateConnectedLines
    });
})();
