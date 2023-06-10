document.addEventListener("DOMContentLoaded", function () {
    const btnGrabber = document.getElementById("btn-text-grabber");
    const btnDebug = document.getElementById("btn-debug-mode");
    const btnParse = document.getElementById("btn-parse");
    const chkTranslation = document.getElementById("chk-translation-mode");
    const btnGrabberLabelModeEnabled = "Leave Grabber Mode";
    const btnGrabberLabelModeDisabled = "Enter Grabber Mode";
    chrome.storage.local.get(['grabberModeEnabled'], function(result) {
        if (result.grabberModeEnabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
        } else {
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
        }
    });
    chrome.storage.local.get(['translationModeEnabled'], function(result) {
        if (result.translationModeEnabled) {
            chkTranslation.checked = true;
        } else {
            chkTranslation.checked = false;
        }
    });

    chkTranslation.addEventListener("change", function () {
        if (chkTranslation.checked) {
            chrome.storage.local.set({translationModeEnabled: true}, function() {
                console.log('NF: Translation mode enabled');
            });
            sendMessage("translateOn");
        } else {
            chrome.storage.local.set({translationModeEnabled: false}, function() {
                console.log('NF: Translation mode disabled');
            });
            sendMessage("translateOff");
        }
    });


    btnGrabber.addEventListener("click", function () {
        chrome.storage
        if (btnGrabber.textContent === btnGrabberLabelModeDisabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
            sendMessage("startPicker");
            chrome.storage.local.set({grabberModeEnabled: true}, function() {
                console.log('NF: Grabber mode enabled');
            });
        } else {
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
            sendMessage("stopPicker");
            chrome.storage.local.set({grabberModeEnabled: false}, function() {
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