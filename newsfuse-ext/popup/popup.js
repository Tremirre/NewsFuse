document.addEventListener("DOMContentLoaded", function () {
    const btnGrabber = document.getElementById("btn-text-grabber");
    const btnDebug = document.getElementById("btn-debug-mode");
    const btnParse = document.getElementById("btn-parse");
    const btnHighlight = document.getElementById("btn-highlight");
    const chkTranslation = document.getElementById("chk-translation-mode");
    const btnGrabberLabelModeEnabled = "Leave Grabber Mode";
    const btnGrabberLabelModeDisabled = "Enter Grabber Mode";
    const btnHighlightEnabled = "Hide Highlights";
    const btnHighlightDisabled = "Show Highlights";
    sendMessage("popupLoaded", function (response) {
            translationMode = response.translationMode;
            grabberMode = response.grabberMode;
            highlightHidden = response.highlightHidden;
            chkTranslation.checked = translationMode;
            btnGrabber.textContent = grabberMode ? btnGrabberLabelModeEnabled : btnGrabberLabelModeDisabled;
            btnHighlight.textContent = highlightHidden ? btnHighlightDisabled : btnHighlightEnabled;
        }
    );
    chkTranslation.addEventListener("change", function () {
        if (chkTranslation.checked) {
            sendMessage("translateOn");
        } else {
            sendMessage("translateOff");
        }
    });


    btnGrabber.addEventListener("click", function () {
        if (btnGrabber.textContent === btnGrabberLabelModeDisabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
            sendMessage("startPicker");
        } else {
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
            sendMessage("stopPicker");
        }
    });

    btnHighlight.addEventListener("click", function () {
        if (btnHighlight.textContent === btnHighlightEnabled) {
            btnHighlight.textContent = btnHighlightDisabled;
            sendMessage("hideHighlights");
        } else {
            btnHighlight.textContent = btnHighlightEnabled;
            sendMessage("showHighlights");
        }
    });

    btnDebug.addEventListener("click", function () {
        sendMessage("debug");
    });

    btnParse.addEventListener("click", function () {
        sendMessage("parse");
    });
});

function sendMessage(message, callback = () => { }) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(
            tabs[0].id, { action: "popupMessage", message: message }
        ).then(callback);
    });
}