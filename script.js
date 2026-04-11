// --- LOGGING FOR DEBUGGING ---
console.log("VOID ENGINE: Initializing...");

// --- GLOBAL STATE ---
window.isGenerating = false;
window.currentChatHistory = [];

// --- 1. SETTINGS PANEL LOGIC (ATTACHED TO WINDOW) ---
window.openSettings = function() {
    console.log("UI: Opening Settings...");
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        
        // Load the stored persona into the textbox
        const savedPrompt = localStorage.getItem('horror_system_prompt');
        const textarea = document.getElementById('system-prompt');
        if (textarea) textarea.value = savedPrompt || "";
    } else {
        alert("Critical Error: 'settings-modal' ID missing in HTML!");
    }
};

window.closeSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
};

window.switchTab = function(tabName) {
    // Hide all tab sections
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    // Reset tab button colors
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('tab-active', 'text-[#a87ffb]');
        el.classList.add('text-gray-400');
    });

    // Show selected tab
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    const activeBtn = document.getElementById(`tab-${tabName}`);
    if (activeBtn) {
        activeBtn.classList.add('tab-active', 'text-[#a87ffb]');
    }
};

window.saveSettings = function() {
    const prompt = document.getElementById('system-prompt').value;
    localStorage.setItem('horror_system_prompt', prompt);
    alert("Persona Bound.");
};

// --- 2. AUTH / OTP LOGIC ---
window.requestOTP = async function() {
    const email = document.getElementById('otp-email').value;
    const btn = document.getElementById('otp-req-btn');

    if (!email || !email.includes('@')) return alert("Enter a valid email.");

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
        alert("Server connection failed.");
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
            alert("Invalid Code.");
        }
    } catch (err) {
        alert("Verification error.");
    }
};

window.logout = function() {
    if (confirm("Disconnect? All local memory will be purged.")) {
        localStorage.clear();
        window.location.reload();
    }
};

// --- 3. CHAT ENGINE ---
window.sendMessage = async function() {
    if (window.isGenerating) return;

    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text);
    input.value = "";
    window.isGenerating = true;
    showTypingIndicator();

    const persona = localStorage.getItem('horror_system_prompt') || "Be a scary AI.";

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, persona: persona })
        });
        const data = await response.json();
        removeTypingIndicator();
        appendMessage('ai', data.reply || "...");
    } catch (err) {
        removeTypingIndicator();
        appendMessage('ai', "The connection was severed.");
    } finally {
        window.isGenerating = false;
    }
};

// --- 4. UI HELPERS ---
function appendMessage(role, text, save = true) {
    const chatBox = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const color = role === 'user' ? 'bg-[#a87ffb] text-black' : 'bg-[#16161a] border border-[#2d2d35] text-[#e2e2e6]';
    
    div.innerHTML = `
        <div class="max-w-[85%] px-6 py-4 rounded-2xl shadow-lg ${color}">
            ${role === 'ai' ? '<p class="text-[10px] font-bold text-[#a87ffb] mb-1">HORROR.AI</p>' : ''}
            <p class="whitespace-pre-wrap">${text}</p>
        </div>
    `;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (save) {
        window.currentChatHistory.push({ role, text });
        localStorage.setItem('horror_memory', JSON.stringify(window.currentChatHistory));
    }
}

function showTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'flex justify-start';
    div.innerHTML = `<div class="bg-[#16161a] border border-[#2d2d35] rounded-2xl px-4 py-2"><div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingIndicator() { document.getElementById('typing-indicator')?.remove(); }

// --- 5. APP STARTUP ---
document.addEventListener('DOMContentLoaded', () => {
    // Restore Memory
    const memory = localStorage.getItem('horror_memory');
    if (memory) {
        window.currentChatHistory = JSON.parse(memory);
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML = "";
        window.currentChatHistory.forEach(m => appendMessage(m.role, m.text, false));
    } else {
        appendMessage('ai', "I have been waiting.", false);
    }
});

// Listener for Enter Key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'user-input') {
        window.sendMessage();
    }
});
