/**
 * Horror.ai - The Final Void Link
 */

// --- Global State ---
let isGenerating = false;

// --- 1. UI & Modal Logic (Must be Global) ---

window.openSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.remove('hidden');
        // Load persona from local storage
        document.getElementById('system-prompt').value = localStorage.getItem('horror_system_prompt') || "";
    }
};

window.closeSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
};

window.switchTab = function(tabId) {
    // Hide all contents
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    // Show target content
    const target = document.getElementById('content-' + tabId);
    if (target) target.classList.remove('hidden');

    // Update Tab Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('tab-active');
        btn.classList.add('text-gray-400');
    });
    const activeBtn = document.getElementById('tab-' + tabId);
    if (activeBtn) {
        activeBtn.classList.add('tab-active');
        activeBtn.classList.remove('text-gray-400');
    }
};

// --- 2. Smart OTP & Auth ---

window.requestOTP = async function() {
    const contactInput = document.getElementById('otp-contact');
    const countryCode = document.getElementById('otp-country').value;
    const contact = contactInput.value.trim();
    
    if (!contact) return alert("Enter an email or phone number.");

    // Detect Device
    const ua = navigator.userAgent.toLowerCase();
    const isAndroid = ua.includes("android");
    const deviceType = isAndroid ? "android" : (ua.includes("iphone") ? "ios" : "desktop");

    try {
        const res = await fetch('/api/otp/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                contact: contact, 
                countryCode: contact.includes('@') ? '' : countryCode,
                device: deviceType
            })
        });

        if (res.ok) {
            alert(contact.includes('@') ? "Check email." : (isAndroid ? "Check WhatsApp." : "Check Messages."));
            // Transition UI
            document.getElementById('otp-input-phase')?.classList.add('hidden');
            document.getElementById('otp-verify-phase')?.classList.remove('hidden');
            localStorage.setItem('pending_contact', contact.includes('@') ? contact : countryCode + contact);
        }
    } catch (e) {
        alert("Void connection failed.");
    }
};

// --- 3. Chat Logic ---

window.sendMessage = async function() {
    if (isGenerating) return;
    
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text);
    input.value = "";
    isGenerating = true;

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: text,
                persona: localStorage.getItem('horror_system_prompt') || ""
            })
        });
        const data = await res.json();
        appendMessage('ai', data.reply);
    } catch (e) {
        appendMessage('ai', "The link to the void has snapped.");
    } finally {
        isGenerating = false;
    }
};

function appendMessage(role, text) {
    const chatBox = document.getElementById('chat-box');
    const msg = document.createElement('div');
    msg.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-6`;
    
    const innerClass = role === 'user' 
        ? 'bg-[#a87ffb] text-black px-6 py-3 rounded-2xl' 
        : 'bg-[#16161a] border border-[#2d2d35] text-white px-6 py-3 rounded-2xl';

    msg.innerHTML = `<div class="${innerClass}">${text}</div>`;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Global Enter Key Listener
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && document.activeElement.id === 'user-input') {
        window.sendMessage();
    }
});
