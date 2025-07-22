async function evaluateText(text) {
    let data = {"text": text};
    const response = await fetch('http://127.0.0.1:5000/evaluate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error("Network response was not ok! ");
    }
    const result = await response.json();
    return result;
}

evaluateText("i am so incredibly insanely silly");