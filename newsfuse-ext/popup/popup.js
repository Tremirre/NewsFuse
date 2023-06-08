document.addEventListener("DOMContentLoaded", function () {
    const btnGrabber = document.getElementById("btn-text-grabber");
    const btnDebug = document.getElementById("btn-debug-mode");
    const btnParse = document.getElementById("btn-parse");
    const btnGrabberLabelModeEnabled = "Leave Grabber Mode";
    const btnGrabberLabelModeDisabled = "Enter Grabber Mode";
    btnGrabber.textContent = btnGrabberLabelModeDisabled;

    btnGrabber.addEventListener("click", function () {
        if (btnGrabber.textContent === btnGrabberLabelModeDisabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
            sendMessage("startPicker");
        } else {
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
            sendMessage("stopPicker");
        }
    });

    btnDebug.addEventListener("click", function () {
        sendMessage("debug");
    });

    btnParse.addEventListener("click", function () {
        sendMessage("parse");
    });
});

function sendMessage(message) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "popupMessage", message: message });
    });
}