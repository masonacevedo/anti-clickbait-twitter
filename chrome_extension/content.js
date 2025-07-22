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


const observer = new MutationObserver((mutations) => {
    console.log("New batch of mutations detected")
    for (const mutation of mutations) {
        console.log("Mutation:")
        console.log(mutation)
    }
    console.log();
});

observer.observe(document.body, {childList: true, subtree: true});