/**
 * Horror.ai - The Smart Void Link
 * Detects OS to optimize OTP delivery
 */

// --- Global State ---
let isGenerating = false;
let currentChatHistory = [];

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("Horror.ai: Void Link Established.");
    
    // 1. Setup Auth UI
    const token = localStorage.getItem('horror_user_token');
    if (token) {
        const contact = localStorage.getItem('horror_user_contact');
        const authStatus = document.getElementById('auth-status');
        if (authStatus) {
            authStatus.innerText = `Bound: ${contact}`;
            authStatus.classList.replace('text-red-500', 'text-[#a87ffb]');
        }
    }

    // 2. Load Memory
    const savedMemory = localStorage.getItem('horror_memory');
    if (savedMemory) {
        currentChatHistory = JSON.parse(savedMemory);
        renderChatBox();
    } else {
        appendMessage('ai', "I have been waiting. What do you seek from the darkness?", false);
    }
});

// --- Device Intelligence ---
function getDeviceType() {
    const ua = navigator.userAgent.toLowerCase();
    if (ua.includes("android")) return "android";
    if (ua.includes("iphone") || ua.includes("ipad")) return "ios";
    return "desktop";
}

// --- Settings & UI ---

window.openSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.getElementById('system-prompt').value = localStorage.getItem('horror_system_prompt') || "";
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
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('tab-active', 'text-[#a87ffb]'));
    
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    const btn = document.getElementById(`tab-${tabName}`);
    if (btn) btn.classList.add('tab-active', 'text-[#a87ffb]');
};

window.saveSettings = function() {
    const prompt = document.getElementById('system-prompt').value;
    localStorage.setItem('horror_system_prompt', prompt);
    alert("Persona Updated.");
};

// --- Smart OTP Logic ---

window.requestOTP = async function() {
    const contact = document.getElementById('otp-contact').value.trim();
    const countryCode = document.getElementById('otp-country').value;
    const btn = document.getElementById('otp-req-btn');
    const device = getDeviceType();

    if (!contact) return alert("Enter your details to proceed.");

    btn.innerText = "Channelling...";
    btn.disabled = true;

    try {
        const res = await fetch('/api/otp/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                contact: contact,
                countryCode: contact.includes('@') ? '' : countryCode,
                device: device // Sending device info to backend
            })
        });

        const data = await res.json();
        if (res.ok) {
            document.getElementById('otp-input-phase').classList.add('hidden');
            document.getElementById('otp-verify-phase').classList.remove('hidden');
            
            // Logic for visual feedback
            const target = contact.includes('@') ? contact : (countryCode + contact.replace(/^0+/, ''));
            localStorage.setItem('pending_target', target);

            // Notify user where to look based on device
            if (!contact.includes('@')) {
                const msg = device === "android" ? "Check your WhatsApp." : "Check your Messages.";
                alert(`Code sent to ${target}. ${msg}`);
            }
        } else {
            alert(data.error || "The void rejected the request.");
        }
    } catch (e) {
        alert("The connection to the server snapped.");
    } finally {
        btn.innerText = "Send Access Code";
        btn.disabled = false;
    }
};

window.verifyOTP = async function() {
    const code = document.getElementById('otp-code').value.trim();
    const target = localStorage.getItem('pending_target');

    try {
        const res = await fetch('/api/otp/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, code })
        });

        const data = await res.json();
        if (data.success) {
            localStorage.setItem('horror_user_token', data.token);
            localStorage.setItem('horror_user_contact', target);
            window.location.reload();
        } else {
            alert("Invalid code. The void does not recognize you.");
        }
    } catch (e) {
        alert("Verification failed.");
    }
};

window.resetOTP = function() {
    document.getElementById('otp-input-phase').classList.remove('hidden');
    document.getElementById('otp-verify-phase').classList.add('hidden');
};

// --- Chat Interface ---

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
        appendMessage('ai', data.reply || "...");
    } catch (err) {
        removeTypingIndicator();
        appendMessage('ai', "The connection to the void has snapped.");
    } finally {
        isGenerating = false;
    }
};

function appendMessage(role, text, save = true) {
    const chatBox = document.getElementById('chat-box');
    if (!chatBox) return;
    
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
            <div class="flex gap-1"><span class="w-1 h-1 bg-gray-500 rounded-full animate-bounce"></span><span class="w-1 h-1 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]"></span><span class="w-1 h-1 bg-gray-500 rounded-full animate-bounce [animation-delay:0.4s]"></span></div>
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
    if (chatBox) {
        chatBox.innerHTML = "";
        currentChatHistory.forEach(msg => appendMessage(msg.role, msg.text, false));
    }
}

document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'user-input') {
        window.sendMessage();
    }
});
