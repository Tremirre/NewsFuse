const NEWSFUSE_FUNC_URL = "http://localhost:7071/api/newsfusebackend"

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    // Handle the message received from content.js
    console.log('NF: Message received in background:', message);
    if (message.action === "classify") {
        console.log("NF: Predicting...")
        const requestBody = {
            "corpus": message.content,
            "omitRewrite": true
        }
        fetch(NEWSFUSE_FUNC_URL, {
            method: 'POST',
            body: JSON.stringify(requestBody),
        }).then(response => {
            return response.json();
        }).then(data => {
            sendResponse(data);
        }).catch(err => {
            sendResponse({error: err});
        });                
        return true;
    }
    sendResponse({ response: `Unknown action ${message.action}` });
});