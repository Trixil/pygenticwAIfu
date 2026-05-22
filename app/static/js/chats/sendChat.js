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

    console.log("before save");
    const saveResponse = await fetch("/api/save-message", {
        method: "POST",
        body: formData
    });

    console.log("before render");
    const renderResponse = await fetch("/render-new-message", {
        method: "POST",
        body: formData
    });
    const newMessageHTML = await renderResponse.text();
    document.querySelector(".chat-bubbles").insertAdjacentHTML("beforeend", newMessageHTML);
})
