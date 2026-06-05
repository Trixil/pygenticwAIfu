const deleteModal = document.querySelector("#deleteLoadoutModal");
const openDeleteButton = document.querySelector(".loadout-delete-button");
const cancelDeleteButton = deleteModal.querySelector(".delete-loadout-modal__button--cancel");
const confirmDeleteButton = deleteModal.querySelector(".delete-loadout-modal__button--delete");

function openDeleteLoadoutModal() {
    deleteModal.classList.add("is-open");
    deleteModal.setAttribute("aria-hidden", "false");
}

function closeDeleteLoadoutModal() {
    deleteModal.classList.remove("is-open");
    deleteModal.setAttribute("aria-hidden", "true");
}

openDeleteButton.addEventListener("click", openDeleteLoadoutModal);
cancelDeleteButton.addEventListener("click", closeDeleteLoadoutModal);

deleteModal.addEventListener("click", function (event) {
    if (event.target === deleteModal) {
        closeDeleteLoadoutModal();
    }
});

confirmDeleteButton.addEventListener("click", async function () {
    console.log("delete confirmed");

    const loadoutID = document.querySelector(".loadout-editor").dataset.loadoutId;

    const response = await fetch("/delete-loadout", {
        headers: {"Content-Type": "application/json"},
        method: "POST",
        body: JSON.stringify({loadoutID})
    });

    closeDeleteLoadoutModal();
    window.location.href = `static`
});