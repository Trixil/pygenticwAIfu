function showPane(paneName)
{
    const characterPane = document.getElementById("character-cards");
    const loadoutPane = document.getElementById("loadout-cards");

    characterPane.classList.add("hidden");
    loadoutPane.classList.add("hidden");

    if (paneName === "character-cards")
    {
        characterPane.classList.remove("hidden");
    }
    if (paneName === "loadout-cards")
    {
        loadoutPane.classList.remove("hidden");
    }
    
}