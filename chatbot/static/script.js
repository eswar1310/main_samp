// script.js

function toggleChatWindow() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.classList.toggle('hidden');
}

function showUrlInput() {
    const urlInput = document.getElementById('url-input');
    urlInput.style.display = 'block';
}

function triggerFileUpload() {
    const fileUpload = document.getElementById('file-upload');
    fileUpload.click();
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/initialize_chatbot/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        displayMessage('System', data.message);
    } catch (error) {
        console.error('Error uploading file:', error);
    }
}

async function handleUrlInput(event) {
    if (event.key === 'Enter') {
        const url = event.target.value;
        const formData = new FormData();
        formData.append('url', url);

        try {
            const response = await fetch('/initialize_chatbot/', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            displayMessage('System', data.message);
        } catch (error) {
            console.error('Error submitting URL:', error);
        }
    }
}

async function handleUserInput(event) {
    if (event.key === 'Enter') {
        const userInput = event.target.value;
        displayMessage('User', userInput);
        event.target.value = '';

        try {
            const response = await fetch('/Ask_The_Question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: userInput })
            });
            const data = await response.json();
            displayMessage('Bot', data.answer);
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }
}

function displayMessage(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
