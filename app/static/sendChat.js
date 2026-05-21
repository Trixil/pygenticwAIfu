const chatBar = document.querySelector(".chat-input-bar")

chatBar.addEventListener("submit", async function () {

    const chatId = window.location.pathname.split("/").filter(Boolean).pop();

    console.log("bruhreally?? the chatid is", chatId)
    const formData = new FormData(chatBar);
    formData.append("chatId", chatId);
    formData.append("role", "User");
    
    // /#/#/ USER NAME NOT IMPLEMENTED YET \#\#\
    // formData.append("sender", username);

    const saveResponse = await fetch("/api/save-message", {
        method: "POST",
        body: formData
    });

    const renderResponse = await fetch("/render-new-message", {
        method: "POST",
        body: formData
    });
    const newMessageHTML = renderResponse.text();
    document.querySelectorAll(".chat-bubbles").insertAdjacentHTML("beforeend", newMessageHTML);
})
