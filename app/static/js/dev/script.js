async function boot()
{
    const box = document.querySelector("#pageid")

    if (!box) {
        return;
    }

    try {
    const response = await fetch("/api/ping");

    if (!response.ok) {
        throw new Error("Bad response");
    }

    const data = await response.json();
    box.textContent = `Backend says: ${data.message}`;
    } catch {
    box.textContent = "Could not connect to backend.";
    }
}

boot();