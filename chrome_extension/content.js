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

async function makeTweetsTransparent(mutations) {
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
}

const observer = new MutationObserver(makeTweetsTransparent);

observer.observe(document.body, {childList: true, subtree: true});

const button = document.createElement('button');
button.textContent = 'Reset Tweets';
button.style.fontSize = '14px';
button.style.padding = '8px 12px';
button.style.backgroundColor = '#dc3545';
button.style.color = 'white';
button.style.border = 'none';
button.style.borderRadius = '6px';
button.style.cursor = 'pointer';
button.style.fontWeight = 'bold';

// Position it in the gap between sidebar and feed
button.style.position = 'fixed';
button.style.zIndex = '999999';
button.style.left = '280px';        // Just past the sidebar width
button.style.top = '100px';         // Below the top nav
button.style.transform = 'translateX(-50%)'; // Center it in the gap

// Optional: make it smaller to fit the narrow space
button.style.fontSize = '12px';
button.style.padding = '6px 10px';

document.body.appendChild(button);

// Add click functionality
button.addEventListener('click', () => {
    document.querySelectorAll('article').forEach(article => {
        if (article.style.opacity){
            article.style.opacity = 1;
        }
    })
});

// Add to page
document.body.appendChild(button);
