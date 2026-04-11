// --- Global State ---
let isGenerating = false;
let currentChatHistory = [];

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('horror_user_token');
    const authStatus = document.getElementById('auth-status');
    
    if (token) {
        const email = localStorage.getItem('horror_user_email');
        authStatus.innerText = `Bound: ${email}`;
        authStatus.classList.replace('text-red-500', 'text-[#a87ffb]');
    }

    // Load Local Memory
    const savedMemory = localStorage.getItem('horror_memory');
    if (savedMemory) {
        currentChatHistory = JSON.parse(savedMemory);
        renderChatBox();
    }
});

// --- OTP Logic ---
window.requestOTP = async function() {
    const email = document.getElementById('otp-email').value;
    const btn = document.getElementById('otp-req-btn');

    if (!email.includes('@')) return alert("Enter a valid email.");

    btn.innerText = "Channelling...";
    btn.disabled = true;

    try {
        const res = await fetch('/api/otp/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        if (res.ok) {
            document.getElementById('otp-email-area').classList.add('hidden');
            document.getElementById('otp-code-area').classList.remove('hidden');
            localStorage.setItem('pending_email', email);
        } else {
            alert("The void rejected this request.");
        }
    } catch (err) {
        alert("Connection failed.");
    } finally {
        btn.innerText = "Send Access Code";
        btn.disabled = false;
    }
};

window.verifyOTP = async function() {
    const code = document.getElementById('otp-code').value;
    const email = localStorage.getItem('pending_email');

    try {
        const res = await fetch('/api/otp/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });

        const data = await res.json();
        if (data.success) {
            localStorage.setItem('horror_user_token', data.token);
            localStorage.setItem('horror_user_email', email);
            window.location.reload();
        } else {
            alert("Wrong code.");
        }
    } catch (err) {
        alert("Verification error.");
    }
};

// --- Chat Functions ---
window.sendMessage = async function() {
    if (isGenerating) return;

    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text);
    input.value = "";
    isGenerating = true;
    showTypingIndicator();

    const persona = localStorage.getItem('horror_system_prompt') || "Speak in riddles.";

    try {
        const res = await fetch('/api/chat', { // Your existing AI route
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, persona })
        });

        const data = await res.json();
        removeTypingIndicator();
        appendMessage('ai', data.reply);
    } catch (err) {
        removeTypingIndicator();
        appendMessage('ai', "The void remains silent.");
    } finally {
        isGenerating = false;
    }
};

// --- UI Helpers ---
function appendMessage(role, text, save = true) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const bgColor = role === 'user' ? 'bg-[#a87ffb] text-black' : 'bg-[#16161a] border border-[#2d2d35] text-[#e2e2e6]';
    
    msgDiv.innerHTML = `
        <div class="max-w-[85%] px-6 py-4 rounded-2xl shadow-lg ${bgColor}">
            ${role === 'ai' ? '<p class="text-[10px] font-bold text-[#a87ffb] mb-1 uppercase tracking-tighter">Horror.ai</p>' : ''}
            <p class="whitespace-pre-wrap leading-relaxed">${text}</p>
        </div>
    `;
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (save) {
        currentChatHistory.push({ role, text });
        localStorage.setItem('horror_memory', JSON.stringify(currentChatHistory));
    }
}

function showTypingIndicator() {
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

function removeTypingIndicator() {
    document.getElementById('typing-indicator')?.remove();
}

function renderChatBox() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = "";
    currentChatHistory.forEach(msg => appendMessage(msg.role, msg.text, false));
}

// Enter key support
document.getElementById('user-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
