import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
DB_PATH = '/app/data/users.db'

# Initialize Database in Volume
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/auth/<type>', methods=['POST'])
def auth(type):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    conn = sqlite3.connect(DB_PATH)
    if type == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?,?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except: return jsonify({"error": "User already exists"}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u,p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Invalid login"}), 401)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    
    # Using Pollinations AI (Free Provider for Gemini/GPT models)
    # We pass the message via URL encoding
    try:
        # Prompt engineering to keep the 'Horror' vibe
        system_prompt = "You are Horror.ai, a dark and mysterious AI. "
        url = f"https://text.pollinations.ai/{system_prompt}{user_msg}?model=openai"
        
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "The void is silent right now. Try again later."})
    except Exception as e:
        return jsonify({"reply": f"Connection to the abyss failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Railway environment port
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
