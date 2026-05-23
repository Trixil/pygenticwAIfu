// clicking the edit button on this message will send the message id to the backend, then the ba

async function editMessage(button)
{
    const messageBubble = button.closest("[data-message-id]");
    const messageId = messageBubble.dataset.messageId;
    const chatId = window.location.pathname.split("/").filter(Boolean).pop();

    const textArea = document.createElement("textarea");
    textArea.classList.add("user-text-area");

    const p = messageBubble.querySelector("p");
    p.replaceWith(textArea);
    textArea.focus();

    textArea.addEventListener("keydown", async function (event) {
        if (event.key === "Enter" && !event.shiftKey)
        {
            newMessageContent = textArea.value;
            
            const response = await fetch("/save-edited-user-message",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ "newMessageContent": newMessageContent,
                                            "messageId": messageId,
                                            "chatId": chatId
                     })
                }
            )
            
            const newP = document.createElement("p");
            newP.classList.add("user-chat-message");
            newP.textContent = newMessageContent;

            textArea.replaceWith(newP);
        }
    })
}