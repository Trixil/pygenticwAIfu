const chatBar = document.querySelector(".chat-input-bar");

async function postJSON(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response;
}

chatBar.addEventListener("submit", async function (event) {
    event.preventDefault();

    const chatId = window.location.pathname.split("/").filter(Boolean).pop();
    const chatBubbles = document.querySelector(".chat-bubbles");

    const messageInput = chatBar.querySelector("[name='chatMessageInput']");
    const userMessage = messageInput.value;

    const userRenderResponse = await postJSON("/render-new-message", {
        chatId: chatId,
        role: "user",
        content: userMessage
    });

    const userMessageHTML = await userRenderResponse.text();
    chatBubbles.insertAdjacentHTML("beforeend", userMessageHTML);

    const userBubbles = document.querySelectorAll(".user-chat-bubble");
    const lastUserBubble = userBubbles[userBubbles.length - 1];

    const userMessageBubble = lastUserBubble.closest("[data-message-id]");
    const userMessageId = userMessageBubble.dataset.messageId;

    await postJSON("/api/save-message", {
        chatId: chatId,
        messageId: userMessageId,
        role: "user",
        content: userMessage
    });

    const llmResponse = await postJSON("/generate-assistant-message", {
        chatId: chatId,
        messageId: userMessageId,
        content: userMessage
    });

    const assistantMessage = await llmResponse.text();

    const assistantRenderResponse = await postJSON("/render-new-message", {
        chatId: chatId,
        role: "assistant",
        content: assistantMessage
    });

    const assistantMessageHTML = await assistantRenderResponse.text();
    chatBubbles.insertAdjacentHTML("beforeend", assistantMessageHTML);

    const assistantBubbles = document.querySelectorAll(".character-chat-bubble");
    const lastAssistantBubble = assistantBubbles[assistantBubbles.length - 1];

    const assistantMessageBubble = lastAssistantBubble.closest("[data-message-id]");
    const assistantMessageId = assistantMessageBubble.dataset.messageId;

    await postJSON("/api/save-message", {
        chatId: chatId,
        messageId: assistantMessageId,
        role: "assistant",
        content: assistantMessage
    });

    messageInput.value = "";
});