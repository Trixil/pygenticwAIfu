const titleEditButton = document.querySelector(".convo-title-edit-button");
const titleHeader = document.querySelector("#convo-title");

if (titleEditButton && titleHeader) {
    titleEditButton.addEventListener("click", function () {
        titleHeader.setAttribute("contenteditable", "true");
        titleHeader.setAttribute("spellcheck", "false");

        titleHeader.focus();

        const range = document.createRange();
        const selection = window.getSelection();

        range.selectNodeContents(titleHeader);
        range.collapse(false);

        selection.removeAllRanges();
        selection.addRange(range);
    });

    async function saveChatTitle() {
        const chatId = window.location.pathname.split("/").filter(Boolean).pop();
        const chatTitle = titleHeader.textContent.trim();

        if (!chatTitle) return;

        const saveResponse = await fetch("/save-chat-title", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                chatId: chatId,
                chatTitle: chatTitle
            })
        });

        if (!saveResponse.ok) {
            console.error("Failed to save chat title:", await saveResponse.text());
        }
    }

    titleHeader.addEventListener("blur", async function () {
        titleHeader.removeAttribute("contenteditable");
        await saveChatTitle();
    });

    titleHeader.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            titleHeader.blur();
        }

        if (event.key === "Escape") {
            event.preventDefault();
            titleHeader.blur();
        }
    });
}