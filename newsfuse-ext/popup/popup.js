document.addEventListener("DOMContentLoaded", function () {
    const btnGrabber = document.getElementById("btn-text-grabber");
    const btnDebug = document.getElementById("btn-debug-mode");
    const btnParse = document.getElementById("btn-parse");
    const btnGrabberLabelModeEnabled = "Leave Grabber Mode";
    const btnGrabberLabelModeDisabled = "Enter Grabber Mode";
    chrome.storage.sync.get(['grabberModeEnabled'], function(result) {
        if (result.grabberModeEnabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
        } else {
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
        }
    });

    btnGrabber.addEventListener("click", function () {
        chrome.storage
        if (btnGrabber.textContent === btnGrabberLabelModeDisabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
            sendMessage("startPicker");
            chrome.storage.sync.set({grabberModeEnabled: true}, function() {
                console.log('NF: Grabber mode enabled');
            });
        } else {
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
            sendMessage("stopPicker");
            chrome.storage.sync.set({grabberModeEnabled: false}, function() {
                console.log('NF: Grabber mode disabled');
            });
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