document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const chatContainer = document.getElementById('chat-container');

    // --- EVENT LISTENERS ---
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (message) {
                displayMessage(message, 'user');
                sendMessageToServer(message);
                messageInput.value = '';
                messageInput.focus();
            }
        });
    }

    document.querySelectorAll('.quick-question').forEach(button => {
        button.addEventListener('click', function () {
            const question = this.dataset.question;
            displayMessage(question, 'user');
            sendMessageToServer(question);
        });
    });

    // --- API CALLS ---
    function sendMessageToServer(message) {
        showTypingIndicator();
        fetch('/chat/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                removeTypingIndicator();
                if (data.error) {
                    displayMessage('Xin lỗi, có lỗi xảy ra: ' + data.error, 'bot');
                } else {
                    displayMessage(data.response, 'bot');
                }
            })
            .catch(error => {
                removeTypingIndicator();
                console.error('Error:', error);
                displayMessage('Xin lỗi, có lỗi xảy ra khi kết nối với máy chủ.', 'bot');
            });
    }

    function loadChatHistory() {
        fetch('/chat/api/chat/history')
            .then(response => response.json())
            .then(data => {
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        displayMessage(msg.content, msg.message_type); // message_type is 'user' or 'bot'
                    });
                } else {
                    displayMessage('Xin chào! Tôi là HSA Chatbot, tôi có thể giúp gì cho bạn?', 'bot');
                }
            })
            .catch(error => {
                console.error('Error loading chat history:', error);
                displayMessage('Xin lỗi, có lỗi khi tải lịch sử trò chuyện.', 'bot');
            });
    }

    // --- UI MANIPULATION ---
    function displayMessage(content, sender) {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message ${sender}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        messageWrapper.appendChild(messageContent);
        chatMessages.appendChild(messageWrapper);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot';
        typingIndicator.id = 'typing-indicator';
        typingIndicator.innerHTML = `
            <div class="message-content">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function scrollToBottom() {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // --- INITIALIZATION ---
    loadChatHistory();
});
