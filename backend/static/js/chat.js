document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const chatContainer = document.getElementById('chat-container');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatHistoryList = document.getElementById('chat-history-list');

    let currentSessionId = null;

    // --- EVENT LISTENERS ---
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (message) {
                sendMessageToServer(message);
                messageInput.value = '';
                messageInput.focus();
            }
        });
    }

    if (newChatBtn) {
        newChatBtn.addEventListener('click', function (e) {
            e.preventDefault();
            createNewSession();
        });
    }

    // --- API CALLS & LOGIC ---
    function sendMessageToServer(message) {
        displayMessage(message, 'user');
        showTypingIndicator();

        // If there's no active session, create one first
        if (!currentSessionId) {
            fetch('/api/chat/session', { method: 'POST' })
                .then(response => response.json())
                .then(sessionData => {
                    currentSessionId = sessionData.session_id;
                    sendChatMessage(message);
                    loadChatSessions(); // Refresh history
                })
                .catch(handleError);
        } else {
            sendChatMessage(message);
        }
    }

    function sendChatMessage(message) {
        fetch(`/api/chat/${currentSessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
            .then(response => response.json())
            .then(data => {
                removeTypingIndicator();
                displayMessage(data.response, 'bot');
            })
            .catch(handleError);
    }

    function loadChatSessions() {
        fetch('/api/chat/sessions')
            .then(response => response.json())
            .then(data => {
                chatHistoryList.innerHTML = '';
                if (data.sessions && data.sessions.length > 0) {
                    data.sessions.forEach(session => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item list-group-item-action';
                        li.textContent = session.title || `Session ${session.id}`;
                        li.dataset.sessionId = session.session_id;
                        li.addEventListener('click', () => {
                            loadSessionHistory(session.session_id);
                        });
                        chatHistoryList.appendChild(li);
                    });
                    // Load the most recent session by default
                    if (!currentSessionId) {
                        loadSessionHistory(data.sessions[0].session_id);
                    }
                } else {
                    createNewSession();
                }
            })
            .catch(handleError);
    }

    function loadSessionHistory(sessionId) {
        currentSessionId = sessionId;
        chatMessages.innerHTML = '';
        showTypingIndicator();
        fetch(`/api/chat/history/${sessionId}`)
            .then(response => response.json())
            .then(data => {
                removeTypingIndicator();
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        displayMessage(msg.content, msg.message_type);
                    });
                } else {
                    displayMessage('Xin chào! Bắt đầu cuộc trò chuyện mới.', 'bot');
                }
            })
            .catch(handleError);
    }

    function createNewSession() {
        currentSessionId = null;
        chatMessages.innerHTML = '';
        displayMessage('Xin chào! Tôi là HSA Chatbot, tôi có thể giúp gì cho bạn?', 'bot');
    }

    function handleError(error) {
        removeTypingIndicator();
        console.error('Error:', error);
        displayMessage('Xin lỗi, có lỗi xảy ra khi kết nối với máy chủ.', 'bot');
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
        typingIndicator.innerHTML = `<div class="message-content"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
        chatMessages.appendChild(typingIndicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    function scrollToBottom() {
        if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // --- INITIALIZATION ---
    loadChatSessions();
});
