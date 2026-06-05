const convoTitleEditButton = document.querySelector(".convo-title-edit-button");
const convoTitleHeader = document.querySelector("#convo-title");

const MAX_CHAT_TITLE_LENGTH = 32;

if (convoTitleEditButton && convoTitleHeader) {
    let originalChatTitle = convoTitleHeader.textContent.trim();
    let isEditingChatTitle = false;

    function getChatIdFromUrl() {
        return window.location.pathname.split("/").filter(Boolean).pop();
    }

    function getCleanChatTitle() {
        return convoTitleHeader.textContent
            .replace(/\s+/g, " ")
            .trim();
    }

    function setChatTitle(title) {
        convoTitleHeader.textContent = title;
    }

    function moveCaretToEnd(element) {
        const range = document.createRange();
        const selection = window.getSelection();

        range.selectNodeContents(element);
        range.collapse(false);

        selection.removeAllRanges();
        selection.addRange(range);
    }

    function showTitleTooLongToast() {
        showToast(
            `Chat titles cannot be more than ${MAX_CHAT_TITLE_LENGTH} characters.`,
            undefined,
            "Chat title too long"
        );
    }

    function startEditingChatTitle() {
        if (isEditingChatTitle) return;

        originalChatTitle = getCleanChatTitle();
        isEditingChatTitle = true;

        convoTitleHeader.setAttribute("contenteditable", "true");
        convoTitleHeader.setAttribute("spellcheck", "false");

        convoTitleHeader.focus();
        moveCaretToEnd(convoTitleHeader);
    }

    function stopEditingChatTitle() {
        isEditingChatTitle = false;
        convoTitleHeader.removeAttribute("contenteditable");
    }

    async function saveChatTitle() {
        const chatId = getChatIdFromUrl();
        const chatTitle = getCleanChatTitle();

        if (!chatTitle) {
            setChatTitle(originalChatTitle);
            return;
        }

        if (chatTitle === originalChatTitle) {
            setChatTitle(originalChatTitle);
            return;
        }

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

            showToast(
                "The chat title could not be saved.",
                undefined,
                "Save failed"
            );

            setChatTitle(originalChatTitle);
            return;
        }

        originalChatTitle = chatTitle;
        setChatTitle(chatTitle);
    }

    convoTitleEditButton.addEventListener("click", startEditingChatTitle);

    convoTitleHeader.addEventListener("beforeinput", function (event) {
        if (!isEditingChatTitle) return;

        const currentText = getCleanChatTitle();
        const selectedText = window.getSelection().toString();

        const incomingText = event.data || "";
        const nextLength =
            currentText.length - selectedText.length + incomingText.length;

        const isTextInput =
            event.inputType === "insertText" ||
            event.inputType === "insertFromPaste" ||
            event.inputType === "insertCompositionText";

        if (!isTextInput) return;

        if (event.inputType === "insertFromPaste") {
            event.preventDefault();

            const pastedText =
                event.clipboardData?.getData("text/plain") || "";

            const remainingLength =
                MAX_CHAT_TITLE_LENGTH - (currentText.length - selectedText.length);

            if (remainingLength <= 0) {
                showTitleTooLongToast();
                return;
            }

            document.execCommand(
                "insertText",
                false,
                pastedText.slice(0, remainingLength)
            );

            if (pastedText.length > remainingLength) {
                showTitleTooLongToast();
            }

            return;
        }

        if (nextLength > MAX_CHAT_TITLE_LENGTH) {
            event.preventDefault();
            showTitleTooLongToast();
        }
    });

    convoTitleHeader.addEventListener("keydown", function (event) {
        if (!isEditingChatTitle) return;

        if (event.key === "Enter") {
            event.preventDefault();
            convoTitleHeader.blur();
            return;
        }

        if (event.key === "Escape") {
            event.preventDefault();
            setChatTitle(originalChatTitle);
            convoTitleHeader.blur();
        }
    });

    convoTitleHeader.addEventListener("blur", async function () {
        if (!isEditingChatTitle) return;

        stopEditingChatTitle();
        await saveChatTitle();
    });
}