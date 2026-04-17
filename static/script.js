function sendMessage() {
    let inputField = document.getElementById("user-input");
    let message = inputField.value.trim();
    if (message === "") return;

    let chatBox = document.getElementById("chat-history");

    chatBox.innerHTML += `<div class="message user-message">${message}</div>`;
    inputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    let formData = new FormData();
    formData.append("user_query", message);

    // Send to Flask backend
    fetch("/ask", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        chatBox.innerHTML += `<div class="message bot-message">${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        chatBox.innerHTML += `<div class="message bot-message">Error connecting to server.</div>`;
    });
}

function pressingKey(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
function clearChat() {
    fetch("/clear", {
        method: "POST"
    })
    .then(response => response.json())
    .then(() => {
        document.getElementById("chat-history").innerHTML =
            '<div class="message bot-message">Chat cleared successfully!</div>';
    });
}
