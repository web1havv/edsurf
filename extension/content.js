// Content script: Extracts main article text using Readability.js
(function() {
    function extractContent() {
        let article = null;
        if (window.Readability) {
            article = new Readability(document.cloneNode(true)).parse();
        }
        if (!article || !article.textContent) {
            article = {
                title: document.title,
                textContent: document.body.innerText
            };
        }
        let author = document.querySelector('meta[name="author"]')?.content || "";
        let date = document.querySelector('time')?.getAttribute('datetime') || "";
        return {
            title: article.title,
            content: article.textContent,
            author,
            date
        };
    }

    chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
        if (msg.action === "extract_content") {
            if (!window.Readability) {
                const script = document.createElement('script');
                script.src = "https://unpkg.com/@mozilla/readability@0.4.4/Readability.js";
                script.onload = () => {
                    sendResponse(extractContent());
                };
                document.head.appendChild(script);
                return true;
            } else {
                sendResponse(extractContent());
            }
        }
    });
})(); 