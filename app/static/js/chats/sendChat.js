const chatBar = document.querySelector(".chat-input-bar")

chatBar.addEventListener("submit", async function (event) {
    event.preventDefault();

    const chatId = window.location.pathname.split("/").filter(Boolean).pop();

    console.log("bruhreally?? the chatid is", chatId)
    const formData = new FormData(chatBar);
    formData.append("chatId", chatId);
    formData.append("role", "user");
    
    // /#/#/ USER NAME NOT IMPLEMENTED YET \#\#\
    // formData.append("sender", username);
    
    console.log("before render");
    const renderResponse = await fetch("/render-new-message", {
        method: "POST",
        body: formData
    });
    
    const newMessageHTML = await renderResponse.text();
    document.querySelector(".chat-bubbles").insertAdjacentHTML("beforeend", newMessageHTML);
    
    const userBubbles = document.querySelectorAll(".user-chat-bubble");
    const lastUserBubble = userBubbles[userBubbles.length - 1];
    
    
    const messageBubble = lastUserBubble.closest("[data-message-id]");
    const messageId = messageBubble.dataset.messageId;
    formData.append("messageId", messageId);
    
    console.log("before save");
    const saveResponse = await fetch("/api/save-message", {
        method: "POST",
        body: formData
    });

    
})
