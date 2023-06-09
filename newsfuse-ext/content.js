console.log("NF: content.js loaded")
var highlightedElement = null;
var stayInPickerMode = false;
var translationMode = false;

const TRANSLATED_COLOR = "rgba(0, 0, 255, 0.4)";
function determinePredictionColor(prediction) {
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

function findBoundingIndices(sentence, element, fromIndex = 0) {
    const firstWord = sentence.split(" ")[0];
    const lastWord = sentence.split(" ").slice(-1)[0].replace('.', '\\.');
    const regex = new RegExp(`${firstWord}\\b.*\\b${lastWord}`, 'g');
    const text = fromIndex === 0 ? element.innerHTML : element.innerHTML.substring(fromIndex + 1);
    const match = regex.exec(text);
    if (match === null) {
        return null;
    }
    const firstIndex = match.index + fromIndex;
    const lastIndex = match.index + match[0].length + fromIndex;
    return [firstIndex, lastIndex];
}

function showClassification(classification, sentences, element) {
    var firstIndex = 0;
    var lastIndex = 0;
    var tagOffset = 0;
    for (const [index, sentence] of sentences.entries()) {
        const sentencePrediction = classification[index];
        const color = determinePredictionColor(sentencePrediction);
        const openTag = `<span class="nf-highlighted-sentence" style="background-color: ${color};"}>`;
        const closeTag = "</span>";
        const replacement = `${openTag}${sentence}${closeTag}`;
        if (element.innerHTML.includes(sentence)) {
            element.innerHTML = element.innerHTML.replace(sentence, replacement);
            continue;
        }
        const boundingIndices = findBoundingIndices(sentence, element, lastIndex + tagOffset);
        if (boundingIndices === null) {
            continue;
        }
        [firstIndex, lastIndex] = boundingIndices;
        const textBefore = element.innerHTML.substring(0, firstIndex);
        const textMiddle = element.innerHTML.substring(firstIndex, lastIndex);
        const textAfter = element.innerHTML.substring(lastIndex);
        const lengthBefore = element.innerHTML.length;
        element.innerHTML = `${textBefore}${openTag}${textMiddle}${closeTag}${textAfter}`
        tagOffset = element.innerHTML.length - lengthBefore;
    }
}
function translateContent(translations, sentences, element) {
    if (translations === null) return;
    var firstIndex = 0;
    var lastIndex = 0;
    for (const [index, translated] of Object.entries(translations)) {
        const sentence = sentences[index];
        const openTag = `<span class="nf-translated-sentence" style="background-color: ${TRANSLATED_COLOR};"}>`;
        const closeTag = "</span>";
        const replacement = `${openTag}${translated}${closeTag}`;
        if (element.innerHTML.includes(sentence)) {
            element.innerHTML = element.innerHTML.replace(sentence, replacement);
            continue;
        }
        const boundingIndices = findBoundingIndices(sentence, element, lastIndex);
        if (boundingIndices === null) {
            continue;
        }
        [firstIndex, lastIndex] = boundingIndices;
        const textBefore = element.innerHTML.substring(0, firstIndex);
        const textAfter = element.innerHTML.substring(lastIndex + 1);
        element.innerHTML = `${textBefore}${replacement}${textAfter}`
    }
}

function stopPickerMode() {
    console.log("NF: stopPickerMode");
    document.removeEventListener("mouseover", mouseoverCallback);
    document.removeEventListener("click", clickPickerCallback);
    if (highlightedElement) {
        highlightedElement.classList.remove("nf-hovered-item");
    }
    highlightedElement = null;
}

async function processElement(element) {
    try {
        const response = await new Promise((resolve, reject) => {
            const action = translationMode ? 'translate' : 'classify';
            chrome.runtime.sendMessage(
                { action: action, content: element.textContent },
                (response) => {
                    if (response.error) {
                        console.error(response);
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
        if (translationMode) {
            var translations = response.translations;
            console.log("NF: Translations:", translations);
            translateContent(translations, sentences, element);
            return;
        }
        showClassification(classification, sentences, element);
    } catch (error) {
        console.error(error.message);
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
    processElement(savedElement);
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
                processElement(element);
            });
        } else if (message.message === "translateOn") {
            translationMode = true;
            console.log("NF: Translation mode enabled");
        } else if (message.message === "translateOff") {
            translationMode = false;
            console.log("NF: Translation mode disabled");
        }
    }
});