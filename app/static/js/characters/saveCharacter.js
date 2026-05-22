const characterForm = document.querySelector(".new-character-form")
const errorMessage = document.querySelector("#character-image-error-message")
const successMessage = document.querySelector("#character-save-success")
const modalToggle = document.querySelector("#new-character-modal-toggle");
const characterCardHTML = document.querySelector("#character-cards");

characterForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    errorMessage.textContent = "";
    successMessage.textContent = "";

    const formData = new FormData(characterForm);
    const response = await fetch("/api/create-character", 
        {   method:"POST",
            body: formData
        })
    
    if (!response.ok) {
        errorMessage.innerHTML = "Save failed."
        return;
    }

    const responseJson = await response.json();
    successMessage.innerHTML = "Saved successfully."

    const characterResponse = await fetch("/add-character-card", 
        {
            method: "POST",
            body: formData
        });
    const newHTML = await characterResponse.text();

    characterCardHTML.insertAdjacentHTML("beforeend", newHTML);
    modalToggle.checked = false;
})