console.log("NF: content.js loaded")
var highlightedElement = null;
var stayInPickerMode = false;

function determineColor(prediction) {
    if (prediction < 0.5) {
        return `rgba(0, 255, 0, ${0.5 - prediction})`;
    }
    return `rgba(255, 0, 0, ${(prediction - 0.5)})`;
}

function mouseoverCallback(event) {
    if (highlightedElement) {
        highlightedElement.classList.remove("nf-hovered-item");
    }
    highlightedElement = event.target;
    highlightedElement.classList.add("nf-hovered-item");
}

function showClassification(classification, sentences, element) {
    for (const [index, sentence] of sentences.entries()) {
        const sentencePrediction = classification[index];
        const color = determineColor(sentencePrediction);
        const openTag = `<span class="nf-highlighted-sentence" style="background-color: ${color};"}>`;
        const closeTag = "</span>";
        const replacement = `${openTag}${sentence}${closeTag}`;
        if (element.innerHTML.includes(sentence)) {
            element.innerHTML = element.innerHTML.replace(sentence, replacement);
            continue;
        }
        const firstWord = sentence.split(" ")[0];
        const lastWord = sentence.split(" ").slice(-1)[0].replace('.', '\\.');
        const regex = new RegExp(`${firstWord}\\b.*\\b${lastWord}`, 'g');
        const match = regex.exec(element.innerHTML);
        if (match === null) {
            continue;
        }
        const firstIndex = match.index;
        const lastIndex = match.index + match[0].length - 1;
        const textBefore = element.innerHTML.substring(0, firstIndex);
        const textMiddle = element.innerHTML.substring(firstIndex, lastIndex + 1);
        const textAfter = element.innerHTML.substring(lastIndex + 1);
        element.innerHTML = `${textBefore}${openTag}${textMiddle}${closeTag}${textAfter}`
    }
}

function stopPickerMode() {
    console.log("NF: stopPickerMode");
    document.removeEventListener("mouseover", mouseoverCallback);
    document.removeEventListener("click", clickPickerCallback);
    highlightedElement.classList.remove("nf-hovered-item");
    highlightedElement = null;
}

async function classifyElementContent(element) {
    try {
        const response = await new Promise((resolve, reject) => {
            chrome.runtime.sendMessage(
                { action: 'classify', content: element.textContent },
                (response) => {
                    if (response.error) {
                        reject(new Error(response.error));
                    } else {
                        resolve(response);
                    }
                }
            );
        });
        var classification = response.classification;
        var sentences = response.sentences;
        console.log("NF: Classification:", classification);
        console.log("NF: Sentences:", sentences);
        showClassification(classification, sentences, element);
    } catch (error) {
        console.log("NF: Error:", error.message);
    }
}

function clickPickerCallback(event) {
    if (!highlightedElement) {
        return;
    }
    console.log("NF: clickPickerCallback");
    var elementContent = highlightedElement.textContent;
    if (elementContent.length > 1000) {
        console.log("NF: Element content too long");
        return;
    }
    highlightedElement.classList.remove("nf-hovered-item");
    const savedElement = highlightedElement;
    classifyElementContent(savedElement);
}

function startPickerMode() {
    document.addEventListener("mouseover", mouseoverCallback);
    document.addEventListener("click", clickPickerCallback);
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.action === "popupMessage") {
        if (message.message === "startPicker") {
            startPickerMode();
        } else if (message.message === "stopPicker") {
            stopPickerMode();
        } else if (message.message === "parse") {
            document.querySelectorAll("p").forEach((element) => {
                classifyElementContent(element);
            });
        }
    }
});