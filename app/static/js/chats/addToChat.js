const selectedCharacterIds = new Set();

function addCharacterToChat() {
    console.log("addCharacterToChat() called");

    const characterCards = document.querySelectorAll(".character-card");
    console.log("Character cards found:", characterCards.length);

    const emptyChatCard = document.querySelector(".empty-chat-card");
    const chatCharacterPane = document.querySelector(".choose-character");

    characterCards.forEach(card => {
        card.addEventListener("click", async () => {
            const characterId = card.dataset.characterId;

            console.log("Character card clicked:", card);
            console.log("Character ID:", characterId);
            console.log("Selected characters before:", [...selectedCharacterIds]);

            if (selectedCharacterIds.has(characterId)) {
                console.log("Character was already selected. Removing:", characterId);

                selectedCharacterIds.delete(characterId);
                card.classList.remove("selected-for-chat");

                document
                    .querySelector(`[data-chat-card-id="${CSS.escape(characterId)}"]`)
                    ?.remove();

                console.log("selectedCharacterIds.length = ", selectedCharacterIds.size)
                if (selectedCharacterIds.size === 0) {
                    emptyChatCard.classList.remove("hidden");
                }

            } else {
                console.log("Character was not selected. Adding:", characterId);

                selectedCharacterIds.add(characterId);
                card.classList.add("selected-for-chat");



                const response = await fetch("/select-character-for-chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ characterId })
                });

                const responseBody = await response.json();

                chatCharacterPane.insertAdjacentHTML("beforeend", responseBody["cardHtml"]);
                
                if (!emptyChatCard.classList.contains("hidden")) {
                    emptyChatCard.classList.add("hidden");
                }
            }

            console.log("Selected characters after:", [...selectedCharacterIds]);
            console.log("Card classes now:", card.className);

            checkChatReadiness();
        });
    });
}

const selectedLoadoutIds = new Set();

function addLoadoutToChat() {
    console.log("addLoadoutToChat() called");

    const loadoutCards = document.querySelectorAll(".loadout-card");
    console.log("Loadout cards found:", loadoutCards.length);

    const emptyLoadoutCard = document.querySelector(".empty-loadout-card");
    const chatLoadoutPane = document.querySelector(".choose-loadout");

    loadoutCards.forEach(card => {
        card.addEventListener("click", async () => {
            const loadoutId = card.dataset.loadoutId;

            console.log("Loadout card clicked:", card);
            console.log("Loadout ID:", loadoutId);
            console.log("Selected loadouts before:", [...selectedLoadoutIds]);

            if (selectedLoadoutIds.has(loadoutId)) {
                console.log("Loadout was already selected. Removing:", loadoutId);

                selectedLoadoutIds.delete(loadoutId);
                card.classList.remove("selected-for-chat");

                document
                    .querySelector(`[data-loadout-card-id="${CSS.escape(loadoutId)}"]`)
                    ?.remove();

                console.log("selectedLoadoutIds.length = ", selectedLoadoutIds.size)
                if (selectedLoadoutIds.size === 0) {
                    emptyLoadoutCard.classList.remove("hidden");
                }

            } else {
                console.log("Loadout was not selected. Adding:", loadoutId);

                let oldLoadoutId = [...selectedLoadoutIds][0];
                console.log("oldLoadoutId is ", oldLoadoutId);
                if (selectedLoadoutIds.size >= 1) {
                    document
                        .querySelector(`[data-loadout-card-id="${CSS.escape(oldLoadoutId)}"]`)
                        ?.remove();
                    selectedLoadoutIds.clear();
                }
                
                selectedLoadoutIds.add(loadoutId);
                card.classList.add("selected-for-chat");

                console.log("loadoutId is ", loadoutId);
                
                const response = await fetch("/select-loadout-for-chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ loadoutId })
                });

                const responseBody = await response.json();

                chatLoadoutPane.insertAdjacentHTML("beforeend", responseBody["cardHtml"]);
                
                if (!emptyLoadoutCard.classList.contains("hidden")) {
                    emptyLoadoutCard.classList.add("hidden");
                }
            }

            console.log("Selected loadouts after:", [...selectedLoadoutIds]);
            console.log("Card classes now:", card.className);

            checkChatReadiness();
        });
    });
}

function checkChatReadiness() {
    const characterIds = [...document.querySelectorAll("[data-chat-card-id]")]
        .map(card => card.dataset.chatCardId);

    const loadoutIds = [...document.querySelectorAll("[data-loadout-card-id]")]
        .map(card => card.dataset.loadoutCardId);

    const isReady = characterIds.length >= 1 && loadoutIds.length === 1;

    document.querySelectorAll(".start-new-chat").forEach(button => {
        button.classList.toggle("start-chat-on-button", isReady);
        button.classList.toggle("start-chat-off-button", !isReady);
    });

    document.querySelectorAll(".start-chat-header").forEach(header => {
        header.classList.toggle("start-chat-on-header", isReady);
        header.classList.toggle("start-chat-off-header", !isReady);
    });
}


document.querySelector(".start-new-chat").addEventListener("click", async () => {
    
    const characterIds = [...document.querySelectorAll("[data-chat-card-id]")]
        .map(card => card.dataset.chatCardId);

    const loadoutId = [...document.querySelectorAll("[data-loadout-card-id]")]
        .map(card => card.dataset.loadoutCardId);

    console.log("characters:", characterIds);
    console.log("loadout:", loadoutId);

    if (characterIds.length >= 1 && loadoutId.length === 1)
    {
        const response = await fetch("/start-new-chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                characterIds: characterIds,
                loadoutId: loadoutId,
            })
        });

        
        const responseBody = await response.json();
        const chatId = responseBody["chatID"];

        window.location.href = `/chat/${chatId}`;

        //const response = await fetch(`/chat/${chatID}`, {
        //    method: "GET",
        //    headers: {
        //        "Content-Type": "application/json",
        //    },
        //    body: JSON.stringify({
        //        chatId: chatId
        //    })
        //});
        //
        //const responseBody = await response.json();
        //const messageHtml = responseBody["messageHTML"];
        //const convoHeadImgHtml = responseBody["convoHeadImgHTML"];
        //const pipelineBubbleHtml = responseBody["pipelineBubbleHTML"];


    }
});
