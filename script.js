console.log("Script initializing...");

// 1. SETTINGS TOGGLE
window.openSettings = function() {
    console.log("Button clicked: Opening settings");
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.remove('hidden');
    } else {
        alert("Error: settings-modal not found in HTML");
    }
};

window.closeSettings = function() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
};

// 2. TAB SWITCHING
window.switchTab = function(tabName) {
    // Hide all
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    // Show one
    const target = document.getElementById('content-' + tabName);
    if (target) target.classList.remove('hidden');
};

// 3. MESSAGING
window.sendMessage = async function() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const text = input.value.trim();

    if (!text) return;

    // Add User Message
    chatBox.innerHTML += `<div class="flex justify-end mb-4"><div class="bg-[#a87ffb] text-black px-4 py-2 rounded-xl">${text}</div></div>`;
    input.value = "";

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        
        // Add AI Message
        chatBox.innerHTML += `<div class="flex justify-start mb-4"><div class="bg-[#16161a] border border-[#2d2d35] text-white px-4 py-2 rounded-xl">${data.reply}</div></div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        console.error("Fetch failed", err);
    }
};

console.log("Script fully loaded.");
