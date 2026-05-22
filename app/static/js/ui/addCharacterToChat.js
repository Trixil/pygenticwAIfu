document.addEventListener("DOMContentLoaded", function () {

    console.log("3")
    const selectedCharacterImgs = document.querySelectorAll("[data-image-character-id]");
    const selectedCharacterIds = new Set([...selectedCharacterImgs].map(function (img) {
        return img.dataset.imageCharacterId;
    }));
    
    console.log("selectedCharacterIds = ", selectedCharacterIds)
    console.log("9")
    const characterCards = document.querySelectorAll(".character-card");
    
    characterCards.forEach( function (card) {
        const characterId = card.dataset.characterId;
        const isSelected = selectedCharacterIds.has(characterId);

        card.classList.toggle("selected-for-chat", isSelected);
        card.classList.toggle("selectable-for-chat", !isSelected);
        console.log(characterId)
    });
    console.log("19")
    
    characterCards.forEach( function (card) {
        card.addEventListener( "click", async () => {
            const characterId = card.dataset.characterId;
            let isSelected = selectedCharacterIds.has(characterId);
            
            console.log("26")
            if (!isSelected)
            {
                selectedCharacterIds.add(characterId);
                isSelected = true;
                const response = await fetch("/render-convo-head-image", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({characterId})
                });
                const convoHeadImgHtml = await response.text();
                document.querySelector(".convo-head-imgs").insertAdjacentHTML("beforeend", convoHeadImgHtml);
                
            }
            else
            {
                selectedCharacterIds.delete(characterId);
                isSelected = false;
                document.querySelector(`[data-image-character-id="${CSS.escape(characterId)}"]`).remove();

            }

            card.classList.toggle("selected-for-chat", isSelected);
            card.classList.toggle("selectable-for-chat", !isSelected);
        });
    });
    // put your startup code here
});

function addCharacterToChat() {
    const characterPicker = document.querySelector(".chat-character-picker");
    characterPicker.classList.toggle("open");
}