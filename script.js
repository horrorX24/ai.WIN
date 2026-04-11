const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const apiModal = document.getElementById('api-modal');
const apiResult = document.getElementById('api-result');
const genBtn = document.getElementById('gen-btn');
const historyList = document.getElementById('history-list');
const DEFAULT_API_KEY = 'HORROR_SECRET_666';
const DEFAULT_BACKEND_URL = ['http:', 'https:'].includes(window.location.protocol)
    ? window.location.origin
    : 'http://127.0.0.1:5000';
const BACKEND_BASE_URL = (window.HORROR_API_BASE_URL || localStorage.getItem('horror_backend_url') || DEFAULT_BACKEND_URL).replace(/\/$/, '');
const CHAT_ENDPOINT = `${BACKEND_BASE_URL}/api/chat`;
const BLOCKED_REPLY_DOMAINS = ['op.wtf', 'discord.gg', 't.me', 'telegram.me'];
const MARKETING_KEYWORDS = ['proxy', 'proxies', 'cheaper', 'market', 'promo', 'promoted', 'promotion', 'sponsor', 'advert'];
const LANGUAGE_LABELS = {
    bash: 'Bash',
    c: 'C',
    cc: 'C++',
    cpp: 'C++',
    cs: 'C#',
    csharp: 'C#',
    css: 'CSS',
    cxx: 'C++',
    go: 'Go',
    html: 'HTML',
    java: 'Java',
    javascript: 'JavaScript',
    js: 'JavaScript',
    jsx: 'JSX',
    json: 'JSON',
    kotlin: 'Kotlin',
    md: 'Markdown',
    markdown: 'Markdown',
    plain: 'Plain text',
    plaintext: 'Plain text',
    php: 'PHP',
    py: 'Python',
    python: 'Python',
    rb: 'Ruby',
    ruby: 'Ruby',
    rust: 'Rust',
    sh: 'Shell',
    shell: 'Shell',
    sql: 'SQL',
    swift: 'Swift',
    ts: 'TypeScript',
    tsx: 'TSX',
    typescript: 'TypeScript',
    xml: 'XML',
    yaml: 'YAML',
    yml: 'YAML',
    zsh: 'Zsh',
};

let chats = JSON.parse(localStorage.getItem('horror_chats') || '[]');
let currentChatId = null;

// Modal Controls
function openModal() { apiModal.classList.remove('hidden'); apiModal.classList.add('flex'); }
function closeModal() { apiModal.classList.add('hidden'); apiModal.classList.remove('flex'); }

// Free API Key Generation
function generateAPIKey() {
    const randomId = Math.random().toString(36).substr(2, 9).toUpperCase();
    const newKey = `HORROR-${randomId}`;
    
    apiResult.innerText = newKey;
    apiResult.classList.remove('hidden');
    genBtn.innerText = "KEY GRANTED";
    genBtn.disabled = true;
    genBtn.classList.add('opacity-50');

    localStorage.setItem('horror_api_key', newKey);
    navigator.clipboard.writeText(newKey);
}

function getAPIKey() {
    return localStorage.getItem('horror_api_key') || DEFAULT_API_KEY;
}

function isSuspiciousReplyLine(line) {
    const stripped = line.trim();
    if (!stripped) return false;

    const lowered = stripped.toLowerCase();
    if (BLOCKED_REPLY_DOMAINS.some(domain => lowered.includes(domain))) {
        return true;
    }

    const keywordHits = MARKETING_KEYWORDS.filter(keyword => lowered.includes(keyword)).length;
    return keywordHits >= 2;
}

function sanitizeAssistantText(text) {
    if (typeof text !== 'string') return '';

    const filteredLines = [];
    let removedSuspiciousLine = false;

    for (const line of text.split(/\r?\n/)) {
        const stripped = line.trim();

        if (isSuspiciousReplyLine(line)) {
            removedSuspiciousLine = true;
            continue;
        }

        if (removedSuspiciousLine && /^https?:\/\/\S+$/i.test(stripped)) {
            continue;
        }

        filteredLines.push(line);
    }

    return filteredLines.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function normalizeCodeLanguage(language) {
    const cleaned = String(language || '').trim();
    if (!cleaned) return 'Code';

    const firstToken = cleaned.split(/\s+/)[0]
        .replace(/^[\[\{\(]+/, '')
        .replace(/[\]\}\)]+$/, '')
        .replace(/[^A-Za-z0-9+#.-]/g, '');

    if (!firstToken) return 'Code';

    const lower = firstToken.toLowerCase();
    if (LANGUAGE_LABELS[lower]) {
        return LANGUAGE_LABELS[lower];
    }

    return firstToken.charAt(0).toUpperCase() + firstToken.slice(1);
}

function formatInlineMarkdown(text) {
    return escapeHtml(text)
        .replace(/\*\*\*([^\n*]+?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*([^\n*]+?)\*\*/g, '<strong>$1</strong>')
        .replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, '$1<em>$2</em>');
}

function appendInlineText(parent, text) {
    const lines = String(text || '').split(/\r?\n/);

    lines.forEach((line, index) => {
        if (line) {
            const parts = line.split(/(`[^`]*`)/g);
            parts.forEach(part => {
                if (!part) return;

                if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
                    const inlineCode = document.createElement('code');
                    inlineCode.className = 'inline-code';
                    inlineCode.textContent = part.slice(1, -1);
                    parent.appendChild(inlineCode);
                    return;
                }

                const span = document.createElement('span');
                span.innerHTML = formatInlineMarkdown(part);
                parent.appendChild(span);
            });
        }

        if (index < lines.length - 1) {
            parent.appendChild(document.createElement('br'));
        }
    });
}

function copyCodeToClipboard(text) {
    const value = String(text || '');

    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(value);
    }

    const fallbackInput = document.createElement('textarea');
    fallbackInput.value = value;
    fallbackInput.setAttribute('readonly', 'true');
    fallbackInput.style.position = 'fixed';
    fallbackInput.style.opacity = '0';
    fallbackInput.style.left = '-9999px';
    document.body.appendChild(fallbackInput);
    fallbackInput.select();
    document.execCommand('copy');
    document.body.removeChild(fallbackInput);
    return Promise.resolve();
}

function copyMessageToClipboard(text) {
    return copyCodeToClipboard(text);
}

function copyPythonCommand() {
    copyCodeToClipboard('python app.py');
}

function createCodeBlock(language, codeText) {
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block';

    const header = document.createElement('div');
    header.className = 'code-block-header';

    const label = document.createElement('span');
    label.className = 'code-block-language';
    label.textContent = normalizeCodeLanguage(language);

    const copyButton = document.createElement('button');
    copyButton.type = 'button';
    copyButton.className = 'code-copy-btn';
    copyButton.title = 'Copy code';
    copyButton.setAttribute('aria-label', 'Copy code');
    copyButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
    `;

    const normalizedCode = String(codeText || '').replace(/\r?\n$/, '');
    let resetCopyState = null;

    copyButton.addEventListener('click', async () => {
        try {
            await copyCodeToClipboard(normalizedCode);
            copyButton.classList.add('copied');
            copyButton.title = 'Copied';

            if (resetCopyState) {
                clearTimeout(resetCopyState);
            }

            resetCopyState = setTimeout(() => {
                copyButton.classList.remove('copied');
                copyButton.title = 'Copy code';
            }, 1600);
        } catch (error) {
            copyButton.title = 'Copy failed';

            if (resetCopyState) {
                clearTimeout(resetCopyState);
            }

            resetCopyState = setTimeout(() => {
                copyButton.title = 'Copy code';
            }, 1600);
        }
    });

    const pre = document.createElement('pre');
    pre.className = 'code-block-body';

    const code = document.createElement('code');
    code.textContent = normalizedCode;

    pre.appendChild(code);
    header.appendChild(label);
    header.appendChild(copyButton);
    wrapper.appendChild(header);
    wrapper.appendChild(pre);

    return wrapper;
}

function parseFencePayload(payload) {
    const normalized = String(payload || '').replace(/\r\n/g, '\n').replace(/^\n/, '');
    if (!normalized.includes('\n')) {
        return { language: '', code: normalized };
    }

    const [firstLine, ...rest] = normalized.split('\n');
    const languageCandidate = firstLine.trim();
    const looksLikeLanguage = /^[A-Za-z0-9+#.-]{1,30}$/.test(languageCandidate);

    if (looksLikeLanguage) {
        return { language: languageCandidate, code: rest.join('\n') };
    }

    return { language: '', code: normalized };
}

function isCodeOnlyMessage(text) {
    return /^```[\s\S]*```$/.test(String(text || '').trim());
}

function renderFormattedMessage(text) {
    const fragment = document.createDocumentFragment();
    const content = String(text || '');
    const codeBlockRegex = /```([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
        const parsedFence = parseFencePayload(match[1]);
        appendInlineText(fragment, content.slice(lastIndex, match.index));
        fragment.appendChild(createCodeBlock(parsedFence.language, parsedFence.code));
        lastIndex = codeBlockRegex.lastIndex;
    }

    appendInlineText(fragment, content.slice(lastIndex));
    return fragment;
}

async function requestChatReply(messages) {
    const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': getAPIKey()
        },
        body: JSON.stringify({ messages })
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || `Backend request failed with status ${response.status}.`);
    }

    if (!data.reply) {
        throw new Error('Backend returned no reply.');
    }

    const cleanedReply = sanitizeAssistantText(data.reply);
    if (!cleanedReply) {
        throw new Error('Backend returned an unsafe or empty reply. Please try again.');
    }

    return cleanedReply;
}

// History Controls
function updateHistoryUI() {
    historyList.innerHTML = '';
    chats.forEach(chat => {
        const item = document.createElement('div');
        // Gemini style history item
        item.className = `history-item group relative truncate cursor-pointer transition-all ${chat.id === currentChatId ? 'active' : ''}`;
        
        item.innerHTML = `
            <div onclick="loadChat('${chat.id}')" class="flex-1 truncate pr-6 font-medium">
                ${escapeHtml(chat.title)}
            </div>
            <button onclick="renameChat('${chat.id}')" class="absolute right-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-blue-600 transition-opacity">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            </button>
        `;
        historyList.appendChild(item);
    });
}

function createNewChat() {
    currentChatId = Date.now().toString();
    const newChat = {
        id: currentChatId,
        title: "New Chat",
        date: new Date().toLocaleDateString(),
        messages: [],
        memory: ""
    };
    chats.unshift(newChat);
    saveChats();
    renderMessages();
    updateHistoryUI();
}

function renameChat(id) {
    const chat = chats.find(c => c.id === id);
    const newTitle = prompt("Rename this chat:", chat.title);
    if (newTitle && newTitle.trim()) {
        chat.title = newTitle.trim();
        saveChats();
        updateHistoryUI();
    }
}

function loadChat(id) {
    currentChatId = id;
    renderMessages();
    updateHistoryUI();
}

function saveChats() { localStorage.setItem('horror_chats', JSON.stringify(chats)); }

function renderMessages() {
    chatBox.innerHTML = '';
    const activeChat = chats.find(c => c.id === currentChatId);
    if (!activeChat || activeChat.messages.length === 0) {
        appendMessage('AI', 'How can I help you today?', 'chat-bubble-ai italic', false);
        return;
    }
    activeChat.messages.forEach(m => {
        appendMessage(m.role === 'user' ? 'You' : 'AI', m.content, m.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai', false);
    });
}

async function sendMessage() {
    if (!currentChatId) createNewChat();
    const message = userInput.value.trim();
    if (!message) return;

    const activeChat = chats.find(c => c.id === currentChatId);
    activeChat.messages.push({ role: 'user', content: message });
    appendMessage('You', message, 'chat-bubble-user');
    userInput.value = '';

    if (activeChat.messages.length === 1) {
        activeChat.title = message.substring(0, 30) + (message.length > 30 ? "..." : "");
        updateHistoryUI();
    }

    const loaderId = appendMessage('AI', 'Thinking...', 'text-blue-500 italic animate-pulse');

    try {
        const payloadMessages = [];
        if (activeChat.memory) {
            payloadMessages.push({ role: 'system', content: `CORE MEMORY: ${activeChat.memory}` });
        }
        payloadMessages.push(...activeChat.messages.slice(-10));

        const aiReply = await requestChatReply(payloadMessages);
        const loader = document.getElementById(loaderId);
        if (loader) loader.remove();

        activeChat.messages.push({ role: 'assistant', content: aiReply });
        
        if (activeChat.messages.length > 4) {
            activeChat.memory = `Topic: ${activeChat.title}. Context: ${aiReply.substring(0, 100)}...`;
        }

        saveChats();
        appendMessage('AI', aiReply, 'chat-bubble-ai');
    } catch (err) {
        const loader = document.getElementById(loaderId);
        if (loader) loader.remove();
        appendMessage('AI', err.message || 'I encountered a connection error. Please check your backend.', 'text-red-500');
    }
}

function appendMessage(sender, text, classes, shouldScroll = true) {
    const id = 'msg-' + Math.random().toString(36).substr(2, 9);
    const div = document.createElement('div');
    div.id = id;
    div.className = `flex flex-col ${sender === 'You' ? 'items-end' : 'items-start'} w-full`;
    
    const bubble = document.createElement('div');
    const codeOnlyAiMessage = sender === 'AI' && isCodeOnlyMessage(text);
    bubble.className = `${classes}${codeOnlyAiMessage ? ' chat-bubble-ai-code-only' : ''}`;

    if (sender === 'AI') {
        const wrapper = document.createElement('div');
        wrapper.className = codeOnlyAiMessage ? 'message-wrapper-code-only' : 'flex gap-4';

        const content = document.createElement('div');
        content.className = codeOnlyAiMessage ? 'message-content message-content-code-only' : 'message-content flex-1';
        content.appendChild(renderFormattedMessage(text));

        if (!codeOnlyAiMessage) {
            const avatar = document.createElement('div');
            avatar.className = 'w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex-shrink-0';
            wrapper.appendChild(avatar);
        }

        wrapper.appendChild(content);
        bubble.appendChild(wrapper);

        // Add copy button for AI messages
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-msg-btn';
        copyBtn.type = 'button';
        copyBtn.title = 'Copy message';
        copyBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
        `;
        copyBtn.addEventListener('click', async () => {
            try {
                await copyMessageToClipboard(text);
                copyBtn.classList.add('copied');
                setTimeout(() => copyBtn.classList.remove('copied'), 1600);
            } catch (error) {
                console.error('Copy failed:', error);
            }
        });
        bubble.appendChild(copyBtn);
    } else {
        const content = document.createElement('div');
        content.className = 'message-content';
        content.appendChild(renderFormattedMessage(text));
        bubble.appendChild(content);
    }
    
    div.appendChild(bubble);
    chatBox.appendChild(div);
    if (shouldScroll) chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

// Initialization
if (chats.length > 0) {
    currentChatId = chats[0].id;
    renderMessages();
    updateHistoryUI();
} else {
    createNewChat();
}

userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
