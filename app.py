import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
DB_PATH = '/app/data/users.db'

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

# --- THE ARENA & GEMINI INTEGRATION ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message')
    # Defaulting to Gemini-style model if not specified
    chosen_model = data.get('model', 'gemini') 
    
    try:
        if chosen_model == 'gemini':
            # Gemini 1.5 Flash logic via Pollinations
            api_url = f"https://text.pollinations.ai/{user_msg}?model=gemini"
        else:
            # Standard Horror.ai logic
            api_url = f"https://text.pollinations.ai/{user_msg}?model=openai"
            
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "The Arena is currently closed. Try again later."})
            
    except Exception as e:
        return jsonify({"reply": f"The void encountered an error: {str(e)}"}), 500

# --- AUTH ROUTES ---
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
        except: return jsonify({"error": "User exists"}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Wrong login"}), 401)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
