// --- 1. State Management ---
let isGenerating = false;
let currentChatHistory = [];

// --- 2. Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already "Logged In" via OTP
    const token = localStorage.getItem('horror_user_token');
    const authStatus = document.getElementById('auth-status');
    
    if (token) {
        const email = localStorage.getItem('horror_user_email');
        if (authStatus) {
            authStatus.innerText = `Bound: ${email}`;
            authStatus.classList.replace('text-red-500', 'text-[#a87ffb]');
        }
    }

    // Load Local Memory from Browser Storage
    const savedMemory = localStorage.getItem('horror_memory');
    if (savedMemory) {
        currentChatHistory = JSON.parse(savedMemory);
        renderChatBox();
    } else {
        // Default intro if no history exists
        appendMessage('ai', "I have been waiting. What do you seek from the darkness?", false);
    }
});

// --- 3. Settings & UI Logic (Attached to Window) ---

window.openSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        // Load the stored persona prompt into the textarea
        document.getElementById('system-prompt').value = localStorage.getItem('horror_system_prompt') || "";
    }
};

window.closeSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }
};

window.switchTab = function(tabName) {
    // Hide all tab content
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    // Reset all tab buttons
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('tab-active', 'text-[#a87ffb]');
        el.classList.add('text-gray-400');
    });

    // Show selected content and highlight button
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    const activeBtn = document.getElementById(`tab-${tabName}`);
    if (activeBtn) {
        activeBtn.classList.add('tab-active', 'text-[#a87ffb]');
        activeBtn.classList.remove('text-gray-400');
    }
};

window.saveSettings = function() {
    const prompt = document.getElementById('system-prompt').value;
    localStorage.setItem('horror_system_prompt', prompt);
    alert("Persona Updated.");
};

// --- 4. OTP Auth Logic ---

window.requestOTP = async function() {
    const emailInput = document.getElementById('otp-email');
    const btn = document.getElementById('otp-req-btn');
    const email = emailInput.value.trim();

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
            alert("The void rejected the request.");
        }
    } catch (err) {
        alert("Failed to reach the server.");
    } finally {
        btn.innerText = "Send Access Code";
        btn.disabled = false;
    }
};

window.verifyOTP = async function() {
    const code = document.getElementById('otp-code').value.trim();
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
            window.location.reload(); // Refresh to update UI
        } else {
            alert("Invalid code.");
        }
    } catch (err) {
        alert("Verification error.");
    }
};

window.logout = function() {
    if (confirm("Disconnect from the void? Local memory will be cleared.")) {
        localStorage.clear();
        window.location.reload();
    }
};

// --- 5. Chat & Messaging ---

window.sendMessage = async function() {
    if (isGenerating) return;

    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text);
    input.value = "";
    isGenerating = true;
    showTypingIndicator();

    const persona = localStorage.getItem('horror_system_prompt') || "Be a mysterious horror entity.";

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, persona })
        });

        const data = await res.json();
        removeTypingIndicator();
        
        if (data.reply) {
            appendMessage('ai', data.reply);
        } else {
            appendMessage('ai', "The whispers are unintelligible.");
        }
    } catch (err) {
        removeTypingIndicator();
        appendMessage('ai', "The connection to the void has snapped.");
    } finally {
        isGenerating = false;
    }
};

function appendMessage(role, text, save = true) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const bgColor = role === 'user' ? 'bg-[#a87ffb] text-black' : 'bg-[#16161a] border border-[#2d2d35] text-[#e2e2e6]';
    
    msgDiv.innerHTML = `
        <div class="max-w-[85%] px-6 py-4 rounded-2xl shadow-lg ${bgColor}">
            ${role === 'ai' ? '<p class="text-[10px] font-bold text-[#a87ffb] mb-1 uppercase tracking-widest">Horror.ai</p>' : ''}
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

// Global listener for Enter key
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'user-input') {
        window.sendMessage();
    }
});
