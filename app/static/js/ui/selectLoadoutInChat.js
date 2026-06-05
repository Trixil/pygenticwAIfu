let selectedLoadoutId = null;

function openLoadoutSelection() {
    const pipelineBubble = document.querySelector(".pipeline-bubble");
    const loadoutPicker = document.querySelector(".chat-loadout-picker");

    pipelineBubble.classList.add("is-selecting-loadout");
    loadoutPicker.classList.add("open");
}

function closeLoadoutSelection() {
    const pipelineBubble = document.querySelector(".pipeline-bubble");
    const loadoutPicker = document.querySelector(".chat-loadout-picker");

    pipelineBubble.classList.remove("is-selecting-loadout");
    loadoutPicker.classList.remove("open");
}

document.addEventListener("DOMContentLoaded", async function () {
    const bubbleLoadoutElement = document.querySelector("[data-bubble-loadout-id]");
    selectedLoadoutId = bubbleLoadoutElement?.dataset.bubbleLoadoutId || null;

    const loadoutCards = document.querySelectorAll(".loadout-card");

    loadoutCards.forEach(function (card) {
        const loadoutId = card.dataset.loadoutId;
        const isSelected = loadoutId === selectedLoadoutId;

        card.classList.toggle("selected-for-chat", isSelected);
        card.classList.toggle("selectable-for-chat", !isSelected);
    });

    loadoutCards.forEach(async function (card) {
        card.addEventListener("click", async function () {
            const loadoutId = card.dataset.loadoutId;

            if (loadoutId === selectedLoadoutId) {
                return;
            }

            if (selectedLoadoutId) {
                const oldCard = document.querySelector(
                    `.loadout-card[data-loadout-id="${CSS.escape(selectedLoadoutId)}"]`
                );

                oldCard?.classList.remove("selected-for-chat");
                oldCard?.classList.add("selectable-for-chat");
            }

            selectedLoadoutId = loadoutId;

            card.classList.add("selected-for-chat");
            card.classList.remove("selectable-for-chat");

            document.querySelector(".loadout-configuration-button").textContent =
                card.querySelector(".loadout-name").textContent;

            if (bubbleLoadoutElement) {
                bubbleLoadoutElement.dataset.bubbleLoadoutId = loadoutId;
            }

            const chatId = window.location.pathname.split("/").filter(Boolean).pop();
            const response = await fetch("/continue-convo-with-loadout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({selectedLoadoutId: selectedLoadoutId,
                    chatId: chatId
                })
            });

            closeLoadoutSelection();
        });
    });
});