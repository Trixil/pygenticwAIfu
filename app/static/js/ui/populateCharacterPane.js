async function populateCharacterPane(characterCard) {
    const characterId = characterCard.dataset.characterId;

    const response = await fetch("/populate-character-pane", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ characterId })
    });

    const responseJson = await response.json();

    const name = responseJson["name"];
    const nickname = responseJson["nickname"];
    const scenario = responseJson["scenario"];
    const description = responseJson["description"];
    const exampleDialogue = responseJson["exampleDialogue"];
    const imageFile = responseJson["imageFile"];

    document.querySelector('textarea[name="name"]').value = name;
    document.querySelector('textarea[name="nickname"]').value = nickname;
    document.querySelector('textarea[name="scenario"]').value = scenario;
    document.querySelector('textarea[name="description"]').value = description;
    document.querySelector('textarea[name="exampleDialogue"]').value = exampleDialogue;

    if (imageFile) {
        const imageResponse = await fetch(imageFile);
        const blob = await imageResponse.blob();

        const actualFilename = imageFile.split("/").pop();

        const file = new File([blob], actualFilename, {
            type: blob.type
        });

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);

        const fileInput = document.querySelector('input[name="characterImage"]');
        fileInput.files = dataTransfer.files;

        fileInput.dispatchEvent(new Event("change", { bubbles: true }));
    }

    document.querySelector(".new-character-form").setAttribute("data-form-character-id", characterId);
}