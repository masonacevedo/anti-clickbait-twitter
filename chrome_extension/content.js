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

async function processTweet(article) {
    const tweetTextElement = article.querySelector('[data-testid="tweetText"]');
    let extractedText = tweetTextElement.textContent.trim();
    const res = await evaluateText(extractedText);
    return res;
}

const observer = new MutationObserver(async (mutations) => {
    let articles = [];
    for (const mutation of mutations) {
        mutation.addedNodes.forEach(node => {
            node.querySelectorAll("article").forEach((article) => {
                articles.push(article);
            })
        })
    }
    
    const promises = articles.map(async (article) => {
        const score = await processTweet(article);
        return score;
    });
    const scores = await Promise.all(promises);
    if (articles.length > 0) {
        for (let i = 0; i < articles.length; i++) {
            articles[i].style.opacity = (1 - scores[i]['score']);
        }
    }
});

observer.observe(document.body, {childList: true, subtree: true});