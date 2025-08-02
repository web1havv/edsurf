chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === "fetch_content") {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, {action: "extract_content"}, (response) => {
                sendResponse(response);
            });
        });
        return true;
    }
}); 