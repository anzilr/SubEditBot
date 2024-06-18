function toggleFormat(command) {
    let inputText = document.getElementById("inputText").value;
    let outputText = document.getElementById("outputText").value;

    outputText = applyTag(outputText, command);

    document.getElementById("outputText").value = outputText;
}

function applyColor() {
    let inputText = document.getElementById("inputText").value;
    let color = document.getElementById("colorPicker").value;
    let outputText = document.getElementById("outputText").value;

    outputText = applyFontColorTag(outputText, color);

    document.getElementById("outputText").value = outputText;
}

function applyTag(text, tag, attribute = '') {
    let openTag = `<${tag}${attribute ? ' ' + attribute : ''}>`;
    let closeTag = `</${tag}>`;

    if (text.includes(openTag) && text.includes(closeTag)) {
        return text.replace(openTag, '').replace(closeTag, '');
    } else {
        return openTag + text + closeTag;
    }
}

function applyFontColorTag(text, color) {
    let fontTagPattern = /<font color=".*?">(.*?)<\/font>/;

    if (fontTagPattern.test(text)) {
        return text.replace(fontTagPattern, `<font color="${color}">$1</font>`);
    } else {
        return `<font color="${color}">${text}</font>`;
    }
}

function copyToClipboard() {
    let outputText = document.getElementById("outputText");
    outputText.select();
    document.execCommand('copy');
    alert('Formatted text copied to clipboard!');
}

// Allowing pasting plain text only
document.getElementById('inputText').addEventListener('input', function() {
    let inputText = document.getElementById("inputText").value;
    document.getElementById("outputText").value = inputText;
});

//<font color="${color}">${inputText}</font>