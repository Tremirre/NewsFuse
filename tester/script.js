const textArea = document.querySelector('textarea');
const resultPreview = document.querySelector('#preview-result');
const endpoint = 'http://127.0.0.1:8000/';
const delayTimeMillis = 1000;

var delayTimer;
textArea.addEventListener('input', () => {
    clearTimeout(delayTimer);
    delayTimer = setTimeout(() => {
        console.log('Predicting...');
        fetch(endpoint, {
            method: 'POST',
            body: JSON.stringify({ corpus: textArea.value, omitRewrite: true})
        }).then(response => response.json()).then(data => {
            resultPreview.innerHTML = ""
            const sentences = data.sentences;
            const classification = data.classification;
            if (sentences.length === 0) return;
            for (let i = 0; i < sentences.length; i++) {
                const sentence = sentences[i];
                const sentenceElement = document.createElement('li');
                sentenceElement.classList.add('sentence');
                textElement = document.createElement('span');
                textElement.innerHTML = sentence;
                classificationElement = document.createElement('span');
                classificationElement.innerHTML = Math.round(classification[i] * 10000) / 10000;
                sentenceElement.appendChild(textElement);
                sentenceElement.appendChild(classificationElement);
                resultPreview.appendChild(sentenceElement);
            }
        }).catch(err => {
            resultPreview.innerHTML = `Error: ${err.message}`;
        });
    }, delayTimeMillis);
});