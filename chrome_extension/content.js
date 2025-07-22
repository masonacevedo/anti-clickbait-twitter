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

function processTweet(article) {
    console.log("analyzing article");

    const tweetTextElement = article.querySelector('[data-testid="tweetText"]');
    console.log('tweetTextElement:', tweetTextElement)
    console.log("tweetTextElement.textContent:", tweetTextElement.textContent);
    console.log("tweetTextElement.textContent.trim():", tweetTextElement.textContent.trim());
}

const observer = new MutationObserver((mutations) => {
    console.log("New batch of mutations detected")
    for (const mutation of mutations) {
        mutation.addedNodes.forEach(node => {
            node.querySelectorAll("article").forEach((article) => {
                processTweet(article)
            })
        })
    }
    console.log();
});

observer.observe(document.body, {childList: true, subtree: true});