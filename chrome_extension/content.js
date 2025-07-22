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

async function makeTweetsTransparent(articles) {
    if (articles.length === 0){
        return
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

const observer = new MutationObserver(async (mutations) => {
    let articles = [];
    for (const mutation of mutations) {
        mutation.addedNodes.forEach(node => {
            if (node.querySelectorAll){
                node.querySelectorAll("article").forEach((article) => {
                    articles.push(article);
                })
            }
        })
    }
    if (articles.length > 0 && transparentMode){
        await makeTweetsTransparent(articles);
    }
});

observer.observe(document.body, {childList: true, subtree: true});

let transparentMode = true;
const button = document.createElement('button');
button.textContent = 'Change to normal mode.';
button.style.fontSize = '14px';
button.style.padding = '8px 12px';
button.style.backgroundColor = '#dc3545';
button.style.color = 'white';
button.style.border = 'none';
button.style.borderRadius = '6px';
button.style.cursor = 'pointer';
button.style.fontWeight = 'bold';

// Optional: make it smaller to fit the narrow space
button.style.fontSize = '12px';
button.style.padding = '6px 10px';

// Add click functionality
button.addEventListener('click', async () => {
    transparentMode = !transparentMode;
    if (transparentMode){
        button.textContent = 'Change to normal mode.';
        let articles = Array.from(document.querySelectorAll('article'));
        await makeTweetsTransparent(articles);
    }
    else{
        button.textContent = 'Change to transparent mode.';
        document.querySelectorAll('article').forEach(article => {
            if (article.style.opacity){
                article.style.opacity = 1;
            }
        })
    }
});


// hacky, but the console will get into an infinite loop
// if we don't have something like this. 
let navButtonAdded = false;
const navObserver = new MutationObserver( (mutations, obs) => {
    for (const mutation of mutations) {
        mutation.addedNodes.forEach(node => {
            nav = document.querySelector('nav[role="navigation"]');
            if (nav && (!navButtonAdded)) {
                nav.appendChild(button);
                navButtonAdded = true;
            }
        })
    }
});
navObserver.observe(document.body, {childList: true, subtree: true})