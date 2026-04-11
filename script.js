let isGenerating = false;
let currentChatHistory = []; // Local Memory Array

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    const savedKey = localStorage.getItem('horror_api_key');
    if (!savedKey) {
        openSettings();
        switchTab('api');
    }
    
    // Load Local Memory
    const savedHistory = localStorage.getItem('horror_memory');
    if (savedHistory) {
        currentChatHistory = JSON.parse(savedHistory);
        renderHistoryList();
        renderChatBox();
    } else {
        appendMessage('ai', "I have been waiting. What do you seek from the darkness?", false);
    }
});

// --- Settings Panel Logic ---
function openSettings() {
    document.getElementById('settings-modal').classList.replace('hidden', 'flex');
    document.getElementById('system-prompt').value = localStorage.getItem('horror_system_prompt') || "";
    
    // Show existing API key if they have one
    const savedKey = localStorage.getItem('horror_api_key');
    if (savedKey) {
        const res = document.getElementById('api-result');
        res.innerText = savedKey;
        res.classList.remove('hidden');
    }
}

function closeSettings() {
    document.getElementById('settings-modal').classList.replace('flex', 'hidden');
}

function switchTab(tabName) {
    // Hide all contents
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    // Remove active state from all buttons
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('tab-active', 'text-[#a87ffb]');
        el.classList.add('text-gray-400');
    });

    // Show selected content
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    // Set active state on button
    const activeBtn = document.getElementById(`tab-${tabName}`);
    activeBtn.classList.add('tab-active', 'text-[#a87ffb]');
    activeBtn.classList.remove('text-gray-400');
}

// --- Account & Auth (Mock/Prep) ---
function handleGoogleLogin() {
    alert("To make Google Sign-in work, you must connect a backend identity provider like Firebase Auth. The UI is ready for your integration!");
    // Example future logic:
    // signInWithPopup(auth, provider).then((result) => { 
    //     document.getElementById('auth-status').innerText = result.user.email;
    //     document.getElementById('auth-status').classList.replace('text-red-500', 'text-green-500');
    // });
}

function saveSettings() {
    const prompt = document.getElementById('system-prompt').value;
    localStorage.setItem('horror_system_prompt', prompt);
    alert("Persona saved to local memory.");
}

function generateAPIKey() {
    const btn = document.getElementById('gen-btn');
    const result = document.getElementById('api-result');
    btn.innerText = "Channelling...";
    btn.disabled = true;

    setTimeout(() => {
        const newKey = "HORROR-" + Math.random().toString(36).substring(2, 15).toUpperCase();
        localStorage.setItem('horror_api_key', newKey);
        result.innerText = newKey;
        result.classList.remove('hidden');
        btn.innerText = "Generated New Key";
        btn.disabled = false;
    }, 1000);
}

function logout() {
    if (confirm("This will purge your API key and local memory. Proceed?")) {
        localStorage.clear();
        window.location.reload();
    }
}

// --- Memory & Chat Logic ---
function saveMemoryLocally() {
    localStorage.setItem('horror_memory', JSON.stringify(currentChatHistory));
    renderHistoryList();
}

function renderHistoryList() {
    const list = document.getElementById('history-list');
    list.innerHTML = "";
    
    // Only show user queries in the sidebar
    const userQueries = currentChatHistory.filter(msg => msg.role === 'user');
    
    if (userQueries.length === 0) {
        list.innerHTML = `<div class="px-4 py-3 text-xs text-gray-600 italic">No memories...</div>`;
        return;
    }

    // Show last 5 queries in sidebar
    userQueries.slice(-5).reverse().forEach(msg => {
        const item = document.createElement('div');
        item.className = "px-4 py-3 text-sm text-gray-400 hover:bg-[#212129] cursor-pointer truncate rounded-xl transition-colors";
        item.innerText = msg.text;
        list.appendChild(item);
    });
}

function renderChatBox() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = "";
    if (currentChatHistory.length === 0) {
        appendMessage('ai', "I have been waiting. What do you seek from the darkness?", false);
    } else {
        currentChatHistory.forEach(msg => appendMessage(msg.role, msg.text, false));
    }
}

function createNewChat() {
    currentChatHistory = [];
    saveMemoryLocally();
    renderChatBox();
}

// --- UI Messaging Helpers ---
function appendMessage(role, text, saveToMemory = true) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const bgColor = role === 'user' ? 'bg-[#a87ffb] text-black' : 'bg-[#16161a] border border-[#2d2d35] text-[#e2e2e6]';
    
    msgDiv.innerHTML = `
        <div class="max-w-[85%] px-6 py-4 rounded-2xl shadow-lg ${bgColor}">
            ${role === 'ai' ? '<p class="gemini-font font-bold text-[#a87ffb] mb-1 text-sm">Horror.ai</p>' : ''}
            <p class="whitespace-pre-wrap leading-relaxed">${text}</p>
        </div>
    `;
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (saveToMemory) {
        currentChatHistory.push({ role, text });
        saveMemoryLocally();
    }
}

function showTypingIndicator() { /* (Same as previous implementation) */
    const chatBox = document.getElementById('chat-box');
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'flex justify-start';
    indicator.innerHTML = `
        <div class="bg-[#16161a] border border-[#2d2d35] rounded-2xl px-4 py-2">
            <div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        </div>
    `;
    chatBox.appendChild(indicator);
    chatBox.scrollTop = chatBox.scrollHeight;
}
function removeTypingIndicator() { document.getElementById('typing-indicator')?.remove(); }

// --- Send API Request ---
async function sendMessage() {
    if (isGenerating) return;

    const input = document.getElementById('user-input');
    const text = input.value.trim();
    const apiKey = localStorage.getItem('horror_api_key');

    if (!text) return;
    if (!apiKey) {
        openSettings();
        switchTab('api');
        return;
    }

    appendMessage('user', text);
    input.value = "";
    isGenerating = true;
    showTypingIndicator();

    const systemPrompt = localStorage.getItem('horror_system_prompt') || "You are a dark, mysterious AI assistant.";

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey },
            body: JSON.stringify({ message: `[SYSTEM INSTRUCTION: ${systemPrompt}]\nUser: ${text}` })
        });

        const data = await response.json();
        removeTypingIndicator();

        if (data.error) appendMessage('ai', `Error: ${data.error}`);
        else appendMessage('ai', data.reply);
        
    } catch (err) {
        removeTypingIndicator();
        appendMessage('ai', "The void is unstable. Check your connection.");
    } finally {
        isGenerating = false;
    }
}

document.getElementById('user-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
