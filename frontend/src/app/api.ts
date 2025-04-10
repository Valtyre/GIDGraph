


export async function getGeneInteractions(text: string): Promise<string> {
    const response = await fetch("https://vercel-python-api-iota.vercel.app/api/greet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: text }), // Use `text` instead of hardcoded "Alice"
    });

    if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
    }

    const data: { message: string } = await response.json();
    console.log(data.message)
    return data.message; // Ensure a string is returned
}
