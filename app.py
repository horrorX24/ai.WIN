import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# --- DATABASE PATH ---
DB_PATH = '/app/data/users.db' if os.path.exists('/app/data') else 'users.db'

def init_db():
    if '/' in DB_PATH: os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

init_db()

# --- SANDBOX PROVIDER LOGIC ---
def get_llm_response(prompt, model_choice):
    """Routes the prompt to different free sandbox providers"""
    
    # 1. Pollinations AI (Gemini / OpenAI / Llama)
    if model_choice in ['gemini', 'openai', 'llama']:
        try:
            url = f"https://text.pollinations.ai/{prompt}?model={model_choice}&cache=false"
            res = requests.get(url, timeout=10)
            if res.status_code == 200: return res.text
        except: pass

    # 2. Blackbox Style / Search Fallback
    try:
        url = f"https://text.pollinations.ai/{prompt}?model=searchgpt"
        res = requests.get(url, timeout=10)
        if res.status_code == 200: return res.text
    except: pass

    return "The sandbox is currently recharging. Try another model."

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    model = data.get('model', 'gemini') # Default to Gemini Sandbox
    
    response = get_llm_response(msg, model)
    return jsonify({"reply": response})

@app.route('/api/auth/<action>', methods=['POST'])
def handle_auth(action):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    conn = sqlite3.connect(DB_PATH)
    if action == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?, ?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except: return jsonify({"error": "Taken"}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Fail"}), 401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
