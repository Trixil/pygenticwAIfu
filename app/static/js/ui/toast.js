function showToast(message, type = "error", title = "Error") {
    let container = document.querySelector("#toast-container");

    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;

    toast.innerHTML = `
        <p class="toast__title">${title}</p>
        <p class="toast__message">${message}</p>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("toast--visible");
    });

    setTimeout(() => {
        toast.classList.remove("toast--visible");

        toast.addEventListener("transitionend", () => {
            toast.remove();
        }, { once: true });
    }, 2600);
}