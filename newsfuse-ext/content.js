console.log("NF: content.js loaded")
var highlightedElement = null;
var translationMode = false;
var grabberMode = false;

const TRANSLATED_COLOR = "rgba(0, 0, 255, 0.4)";
const TRANSLATED_CLASS = "nf-translated-sentence";
const HIGHLIGHTED_CLASS = "nf-highlighted-sentence";
const ELEMENT_VISITED_CLASS = "nf-visited-element";

const REPLACEMENT_MAP = {
    "\xa0": " ",
}

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

function normalizeSentence(sentence) {
    var normalized = sentence;
    for (const [key, value] of Object.entries(REPLACEMENT_MAP)) {
        normalized = normalized.replace(key, value);
    }
    return normalized;
}

function findMatch(sentence, text) {
    const sentenceNormalized = normalizeSentence(sentence);
    const firstWord = sentenceNormalized.split(" ")[0];
    const lastWord = sentenceNormalized.split(" ").slice(-1)[0].replace('.', '\\.');

    const sentenceMidLength = sentence.length - firstWord.length - lastWord.length;
    const regex = new RegExp(`${firstWord}.{${sentenceMidLength},}${lastWord}`, 'g');
    var match = regex.exec(text);

    if (match !== null) {
        return match;
    }

    if (lastWord.slice(-1)[0] === ".") {
        // Retry in case the sentence ends with a closing tag between last word and period
        const regex = new RegExp(`${firstWord}.{${sentenceMidLength},}>\\.`, 'g');
        match = regex.exec(text);
        return match;
    }

    return null;
}

function findBoundingIndices(sentence, element, fromIndex = 0) {
    const text = element.innerHTML.substring(fromIndex);
    var match = findMatch(sentence, text);
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
        const openTag = `<span class="${HIGHLIGHTED_CLASS}" style="background-color: ${color};"}>`;
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
    grabberMode = false;
    document.removeEventListener("mouseover", mouseoverCallback);
    document.removeEventListener("click", clickPickerCallback);
    if (highlightedElement) {
        highlightedElement.classList.remove("nf-hovered-item");
    }
    highlightedElement = null;
}

async function processElement(element) {
    if (element.classList.contains(ELEMENT_VISITED_CLASS)) {
        console.warn("NF: Element already visited");
        return;
    }
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
        element.classList.add(ELEMENT_VISITED_CLASS);
        if (translationMode && response.translations) {
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
    grabberMode = true;
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
        } else if (message.message === "popupLoaded") {
            sendResponse({ translationMode: translationMode , grabberMode: grabberMode});
        }
    }
});