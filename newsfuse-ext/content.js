console.log("content.js loaded")
var highlightedElement = null;

function mouseoverCallback(event) {
    if (highlightedElement) {
        highlightedElement.classList.remove("nf-hovered-item");
    }
    highlightedElement = event.target;
    highlightedElement.classList.add("nf-hovered-item");
}

function stopPickerMode() {
    console.log("stopPickerMode");
    document.removeEventListener("mouseover", mouseoverCallback);
    document.removeEventListener("click", clickPickerCallbakc);
}

function clickPickerCallbakc(event) {
    if (!highlightedElement) {
        return;
    }
    var elementContent = highlightedElement.textContent;
    console.log(elementContent);
    highlightedElement.classList.remove("nf-hovered-item");
    highlightedElement = null;
    stopPickerMode();
}


function startPickerMode() {
    document.addEventListener("mouseover", mouseoverCallback);
    document.addEventListener("click", clickPickerCallbakc);
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.action === "popupMessage") {
        if (message.message === "picker") {
            startPickerMode();
        }
    }
});