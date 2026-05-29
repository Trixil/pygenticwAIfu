document.addEventListener("DOMContentLoaded", function () {
    const allAgents = document.querySelectorAll(".agent-card");
    allAgents.forEach( agent => {
        agent.querySelector("agent-card__name").addEventListener("click", function () {
            showAgentPane(agent);
        });
    })

    const pane = document.querySelector(".loadout-editor-pane");
    const tabButtons = pane.querySelectorAll(".loadout-editor-pane--tab");

    tabButtons.forEach(button => {
        button.addEventListener("click", function () {
            pane.dataset.activeTab = button.dataset.tab;
        });
    });
});

const allAgents = [...document.querySelectorAll("[data-agent-id]")];

const agentConfigs = Object.fromEntries(
    allAgents.map(agent => [
        agent.dataset.agentId,
        {
            agentName: "",
            agentConfiguration: {
                agentId: agent.dataset.agentId,
                agentInstructions: "",
                characterInput: false,
                scenario: false,
                carryOver: false,
                parents: new Set(),
                children: new Set(),
                agentLLMConfig: {
                    LLMName: "",
                    temp: 1,
                    maxTokens: 4000,
                    topP: 1
                }

            }
        }
    ])
);

function createDefaultAgentConfig(agentId, agentName = "") {
    return {
        agentName: agentName,
        agentConfiguration: {
            agentId: agentId,
            agentInstructions: "",
            characterInput: false,
            scenario: false,
            carryOver: false,
            parents: [],
            children: [],
            agentLLMConfig: {
                LLMName: "GPT-4.1",
                temp: 1,
                maxTokens: 4000,
                topP: 1
            }
        }
    };
}
