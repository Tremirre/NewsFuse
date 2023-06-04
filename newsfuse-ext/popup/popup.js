document.addEventListener("DOMContentLoaded", function () {
    const btnGrabber = document.getElementById("btn-text-grabber");
    const btnDebug = document.getElementById("btn-debug-mode");

    btnGrabber.addEventListener("click", function () {
        sendMessage("picker");
    });

    btnDebug.addEventListener("click", function () {
        sendMessage("debug");
    });
});

function sendMessage(message) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "popupMessage", message: message });
    });
}