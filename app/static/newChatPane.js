function showNewChatPane()
{
    const activeChatPane = document.querySelector(".active-chat-pane");
    activeChatPane.classList.add("hidden");

    const newChatPane = document.querySelector(".new-chat-pane");
    newChatPane.classList.remove("hidden");

    const characterCards = document.querySelectorAll(".character-card");
    const loadoutCards = document.querySelectorAll(".loadout-card");
    
    characterCards.forEach(card => {
        card.classList.add("selectable-for-chat");
    });
    
    loadoutCards.forEach(card => {
        card.classList.add("selectable-for-chat");
    });

    const editButtons = document.querySelectorAll(".character-edit-button");
    editButtons.forEach(button => {
        button.classList.add("hidden")
    });
}

function showActiveChatPane()
{
    const newChatPane = document.querySelector(".new-chat-pane");
    newChatPane.classList.add("hidden");

    const activeChatPane = document.querySelector(".active-chat-pane");
    activeChatPane.classList.remove("hidden");

    const characterCards = document.querySelectorAll(".character-card");
    const loadoutCards = document.querySelectorAll(".loadout-card");
    
    characterCards.forEach(card => {
        card.classList.remove("selectable-for-chat");
    });
    
    loadoutCards.forEach(card => {
        card.classList.remove("selectable-for-chat");
    });

    const editButtons = document.querySelectorAll(".character-edit-button");
    editButtons.forEach(button => {
        button.classList.remove("hidden")
    });
}

function removeSelected()
{
    const selectedCards = document.querySelectorAll(".selected-for-chat");
    selectedCards.forEach( card => {
        card.classList.remove("selected-for-chat");
    })
}