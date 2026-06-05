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

    for (const [key, value] of formData.entries()) {
        console.log(key, value);
    }
    
    if (characterForm.hasAttribute("data-form-character-id"))
    {
        const characterID = characterForm.dataset.characterId;
        characterForm.append("characterID", characterID);
        const response = await fetch("/api/update-character", 
            {   method:"POST",
                body: formData
            })
        
        if (!response.ok) {
            errorMessage.innerHTML = "Save failed."
            return;
        }
        
    }
    else
    {
        const response = await fetch("/api/create-character", 
            {   method:"POST",
                body: formData
            })
        
        if (!response.ok) {
            errorMessage.innerHTML = "Save failed."
            return;
        }
        const responseJson = await response.json();
        const characterID = responseJson["characterID"]
        formData.append("characterID", characterID);
        const characterResponse = await fetch("/add-character-card", 
            {
                method: "POST",
                body: formData
            });
        const newHTML = await characterResponse.text();
        
        characterCardHTML.insertAdjacentHTML("beforeend", newHTML);
    }
    successMessage.innerHTML = "Saved successfully."
    characterForm.reset();

    modalToggle.checked = false;
})