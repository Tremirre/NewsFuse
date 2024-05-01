document.addEventListener("DOMContentLoaded", function () {
    const btnGrabber = document.getElementById("btn-text-grabber");
    const btnParse = document.getElementById("btn-parse");
    const chkHighlight = document.getElementById("chk-show-highlight");
    const chkTranslation = document.getElementById("chk-translation-mode");
    const btnGrabberLabelModeEnabled = "Leave Grabber Mode";
    const btnGrabberLabelModeDisabled = "Enter Grabber Mode";
    sendMessage("popupLoaded", function (response) {
            translationMode = response.translationMode;
            grabberMode = response.grabberMode;
            highlightHidden = response.highlightHidden;
            chkTranslation.checked = translationMode;
            btnGrabber.textContent = grabberMode ? btnGrabberLabelModeEnabled : btnGrabberLabelModeDisabled;
        }
    );
    chkTranslation.addEventListener("change", function () {
        if (chkTranslation.checked) {
            sendMessage("translateOn");
        } else {
            sendMessage("translateOff");
        }
    });

    chkHighlight.addEventListener("change", function () {
        if (chkHighlight.checked) {
            sendMessage("showHighlights");
        } else {
            sendMessage("hideHighlights");
        }
    });


    btnGrabber.addEventListener("click", function () {
        if (btnGrabber.textContent === btnGrabberLabelModeDisabled) {
            btnGrabber.textContent = btnGrabberLabelModeEnabled;
            btnParse.disabled = true;
            sendMessage("startPicker");
        } else {
            btnParse.disabled = false;
            btnGrabber.textContent = btnGrabberLabelModeDisabled;
            sendMessage("stopPicker");
        }
    });
    
    btnParse.addEventListener("click", function () {
        sendMessage("parse");
        btnParse.disabled = true;
    });
});

function sendMessage(message, callback = () => { }) {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(
            tabs[0].id, { action: "popupMessage", message: message }
        ).then(callback);
    });
}