async function populateCharacterPane(characterCard) {
    document.querySelector(".new-character-actions")
        .querySelector(".new-character-primary")
        .textContent = "Update Character";
    
    document.querySelector(".new-character-modal")
        .querySelector("#new-character-title")
        .textContent = "Update Character";
    const characterId = characterCard.dataset.characterId;

    const response = await fetch("/populate-character-pane", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ characterId })
    });

    if (!response.ok) {
        console.error("Failed to populate character pane.");
        return;
    }

    const responseJson = await response.json();

    const name = responseJson["name"];
    const nickname = responseJson["nickname"];
    const scenario = responseJson["scenario"];
    const description = responseJson["description"];
    const exampleDialogue = responseJson["exampleDialogue"];
    const imageFile = responseJson["imageFile"];

    const characterForm = document.querySelector(".new-character-form");

    document.querySelector('input[name="characterName"]').value = name;
    document.querySelector('input[name="nickname"]').value = nickname;
    document.querySelector('textarea[name="scenario"]').value = scenario;
    document.querySelector('textarea[name="description"]').value = description;
    document.querySelector('textarea[name="exampleDialogue"]').value = exampleDialogue;

    const fileInput = document.querySelector('input[name="characterImage"]');
    fileInput.value = "";

    if (imageFile) {
        const actualFilename = imageFile.split(/[\\/]/).pop();
        characterForm.setAttribute("data-existing-image-file", actualFilename);
    } else {
        characterForm.removeAttribute("data-existing-image-file");
    }

    characterForm.setAttribute("data-form-character-id", characterId);
}