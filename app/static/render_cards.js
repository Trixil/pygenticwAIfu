async function fetchCharacterCards() {
    const response = await fetch("/character-cards");
    const allCardsHtml = await response.text();
    document.getElementById("character-cards").innerHTML = allCardsHtml;
}

fetchCharacterCards();
