async function showLoadoutEditor()
{
    document.querySelector(".layout").classList.toggle("config-expand-hide");
    document.querySelector(".layout").classList.toggle("config-expand-widen");

    document.querySelector(".loadout-editor").classList.toggle("hidden");
}

async function startLoadoutEditor()
{
    allAgents = document.querySelectorAll("[data-agent-id]");
    let isDragging = false;
    allAgents.forEach( agent => {
        agent.addEventListener("pointerdown", async function () {
            isDragging = true;
            agent.addEventListener("pointermove", async function (event) {
                const rect = agent.getBoundingClientRect();

                const x = event.clientX;
                const y = event.clientY;

                agent.style.left = agent.style.left + rect.left
            })
        })
    })
}