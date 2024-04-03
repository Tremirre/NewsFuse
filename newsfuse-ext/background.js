const NEWSFUSE_FUNC_URL = "http://127.0.0.1:8000/"

function fetchToNewsFuseBackend(requestBody, sendResponse) {
    fetch(NEWSFUSE_FUNC_URL, {
        method: 'POST',
        body: JSON.stringify(requestBody),
    }).then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} (${response.statusText})`);
        }
        return response.json();
    }).then(data => {
        sendResponse(data);
    }).catch(err => {
        sendResponse({error: err.message});
    });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    // Handle the message received from content.js
    console.log('NF: Message received in background:', message);
    if (message.action === "classify") {
        console.log("NF: Predicting...")
        const requestBody = {
            "corpus": message.content,
            "omitRewrite": true
        }
        fetchToNewsFuseBackend(requestBody, sendResponse);    
        return true;
    } else if (message.action === "translate") {
        console.log("NF: Translating...")
        const requestBody = {
            "corpus": message.content,
            "omitRewrite": false
        }
        fetchToNewsFuseBackend(requestBody, sendResponse);
        return true;
    }
    sendResponse({ response: `Unknown action ${message.action}` });
});