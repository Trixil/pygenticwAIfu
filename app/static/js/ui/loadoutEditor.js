async function showLoadoutEditor()
{
    document.querySelector(".layout").classList.toggle("config-expand-hide");
    document.querySelector(".layout").classList.toggle("config-expand-widen");

    document.querySelector(".loadout-editor").classList.toggle("hidden");
}
async function startLoadoutEditor() {
    const allAgents = [...document.querySelectorAll("[data-agent-id]")];

    const allChildren = Object.fromEntries(
        allAgents.map(agent => [agent.dataset.agentId, new Set()])
    );

    let isDraggingAgent = false;
    let isDraggingLine = false;
    let draggedAgent = null;
    let draggedLine = null;
    let activeSvg = null;
    let xOffset = 0;
    let yOffset = 0;
    const allConfigsById = Object.fromEntries(
        allAgents.map(agent => [
            agent.dataset.agentId,
            {
                name: "",
                id: agent.dataset.agentId,
                configuration: {
                    useCharacter: false,
                    useImage: false,
                    usePreviousOutput: false,
                    inputs: new Set(),
                    outputs: new Set()
                }
            }
        ])
    );
    
    allAgents.forEach(agent => {
        const agentId = agent.dataset.agentId;
        const agentOutput = agent.querySelector(".agent-port--out");
        const agentInput = agent.querySelector(".agent-port--in");
        const svgList = agent.querySelector(".wire-layer");

        const checkboxButtons = agent.querySelectorAll(".agent-card__button--flat");

        const carryOver = agent.querySelector(".agent-carryover")
        const scenario = agent.querySelector(".agent-scenario")
        const characterInput = agent.querySelector(".agent-character-input");



        checkboxButtons.forEach(function (button) {
            button.addEventListener("pointerdown", function (event) {
                event.stopPropagation();
            });

            button.addEventListener("click", function (event) {
                event.stopPropagation();
                button.classList.toggle("agent-card__button--checked");
            });
        });

        agent.addEventListener("pointerdown", function (downEvent) {
            const outRect = agentOutput.getBoundingClientRect();

            const clickedOutput =
                downEvent.clientX >= outRect.left &&
                downEvent.clientX <= outRect.right &&
                downEvent.clientY >= outRect.top &&
                downEvent.clientY <= outRect.bottom;

            if (clickedOutput) return;

            isDraggingAgent = true;
            draggedAgent = agent;

            const rect = agent.getBoundingClientRect();

            xOffset = downEvent.clientX - rect.left;
            yOffset = downEvent.clientY - rect.top;

            agent.setPointerCapture(downEvent.pointerId);
        });

        agentOutput.addEventListener("pointerdown", function (downEvent) {
            downEvent.stopPropagation();

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");

            draggedLine = line;
            activeSvg = svgList;
            isDraggingLine = true;

            const outRect = agentOutput.getBoundingClientRect();
            const svgRect = activeSvg.getBoundingClientRect();

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
            line.setAttribute("data-agent-start", agent.dataset.agentId);

            activeSvg.appendChild(line);
        });

        agentInput.addEventListener("pointerup", function (upEvent) {
            if (isDraggingLine && draggedLine && activeSvg) {

                const startAgentId = draggedLine.getAttribute("data-agent-start");
                const endAgentId = agent.dataset.agentId;
                if (isLoop(startAgentId, endAgentId, allChildren) || startAgentId === endAgentId)
                    return;

                const svgRect = activeSvg.getBoundingClientRect();
                const inRect = agentInput.getBoundingClientRect();

                const startX = Number(draggedLine.getAttribute("x1"));
                const startY = Number(draggedLine.getAttribute("y1"));

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

                activeSvg.appendChild(connectorLine);

                allAgents[startAgentId].add(endAgentId);
            }
        });
        
        carryOver.addEventListener("pointerdown", function (downEvent) {
            const isChecked = carryoverButton.classList.contains("agent-card__button--checked");
        });

        scenario.addEventListener("pointerdown", function (downEvent) {
            const isChecked = scenario.classList.contains("agent-card__button--checked");
        });

        characterInput.addEventListener("pointerdown", function (downEvent) {
            const isChecked = characterInput.classList.contains("agent-card__button--checked");
        });
    });

    document.addEventListener("pointermove", function (moveEvent) {
        if (!isDraggingAgent && !isDraggingLine) return;

        if (isDraggingAgent && draggedAgent) {
            const parentRect = draggedAgent.offsetParent.getBoundingClientRect();

            draggedAgent.style.left = `${moveEvent.clientX - parentRect.left - xOffset}px`;
            draggedAgent.style.top = `${moveEvent.clientY - parentRect.top - yOffset}px`;
        }

        if (isDraggingLine && draggedLine && activeSvg) {
            const svgRect = activeSvg.getBoundingClientRect();

            draggedLine.setAttribute("x2", moveEvent.clientX - svgRect.left);
            draggedLine.setAttribute("y2", moveEvent.clientY - svgRect.top);
        }
    });

    document.addEventListener("pointerup", function () {
        if (draggedLine != null) {
            draggedLine.remove();
        }

        isDraggingAgent = false;
        draggedAgent = null;

        isDraggingLine = false;
        draggedLine = null;
        activeSvg = null;
    });
}

function isLoop(source, destination, kindergarten)
{
    destinationChildren = [...kindergarten[destination]];
    if (destinationChildren.has(source))
    {
        return true;
    }

    const hasLoop = [...destinationChildren].some(function (child) {
        return isLoop(source, child);
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