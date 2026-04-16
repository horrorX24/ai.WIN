let currentChatId = null; // Track the active chat session
let history = JSON.parse(localStorage.getItem('horror_history') || '[]');

async function sendMessage() {
    const input = document.getElementById('user-input');
    const box = document.getElementById('chat-box');
    const msg = input.value.trim();
    if(!msg) return;

    // Show User Message
    box.innerHTML += `<div class="flex justify-end"><div class="bg-[#a87ffb] text-black p-3 rounded-xl text-sm max-w-xs">${msg}</div></div>`;
    input.value = "";
    
    const typingId = "typing-" + Date.now();
    box.innerHTML += `<div id="${typingId}" class="text-gray-500 text-xs italic">Horror is thinking...</div>`;
    box.scrollTop = box.scrollHeight;

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        document.getElementById(typingId).remove();
        
        // Show AI Message
        box.innerHTML += `<div class="flex justify-start"><div class="bg-[#1a1a24] border border-[#2d2d35] p-3 rounded-xl text-sm max-w-xs">${data.reply}</div></div>`;

        // SIDEBAR LOGIC: Only save new chat if this is the FIRST message
        if (currentChatId === null) {
            currentChatId = Date.now(); // Create a unique ID for this session
            history.unshift({ 
                id: currentChatId, 
                title: msg.substring(0, 25) + "...", 
                content: box.innerHTML 
            });
        } else {
            // Update the existing chat content in history
            const index = history.findIndex(item => item.id === currentChatId);
            if (index !== -1) history[index].content = box.innerHTML;
        }
        
        localStorage.setItem('horror_history', JSON.stringify(history));
        updateHistoryUI();

    } catch (e) {
        document.getElementById(typingId).innerText = "The connection was severed.";
    }
    box.scrollTop = box.scrollHeight;
}

function createNewChat() {
    document.getElementById('chat-box').innerHTML = "";
    currentChatId = null; // Reset ID so the next message starts a new chat
}

function loadChat(id) {
    const chat = history.find(item => item.id === id);
    if (chat) {
        document.getElementById('chat-box').innerHTML = chat.content;
        currentChatId = chat.id; // Set active ID to this old chat
    }
}

function updateHistoryUI() {
    const container = document.getElementById('chat-history');
    container.innerHTML = history.map(item => `
        <div class="sidebar-item p-3 rounded-lg text-xs truncate text-gray-400 ${item.id === currentChatId ? 'bg-[#1a1a24] border-l-2 border-[#a87ffb]' : ''}" 
             onclick="loadChat(${item.id})">
            ${item.title}
        </div>
    `).join('');
}
