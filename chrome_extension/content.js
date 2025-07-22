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

const button = document.createElement('button');
button.textContent = 'MAKE TWEETS NORMAL';
button.style.fontSize = '24px';
button.style.padding = '20px 40px';
button.style.backgroundColor = '#dc3545';
button.style.color = 'white';
button.style.border = 'none';
button.style.borderRadius = '10px';
button.style.cursor = 'pointer';
button.style.fontWeight = 'bold';
button.style.position = 'absolute'; // or 'absolute'
button.style.zIndex = '99999';

// Add click functionality
button.addEventListener('click', () => {
    alert('Button clicked!');
    document.querySelectorAll('article').forEach(article => {
        if (article.style.opacity){
            article.style.opacity = 1;
        }
    })
});

// Add to page
document.body.appendChild(button);
