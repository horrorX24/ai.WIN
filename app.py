import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# --- DATABASE SETUP ---
# Path for the persistent volume
DB_PATH = '/app/data/users.db'

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Volume not found, using local fallback: {e}")

init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# --- ARENA / GEMINI AI LOGIC ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message')
    model = data.get('model', 'openai') # Switch between gemini/openai
    
    try:
        # Using Pollinations as the free provider
        api_url = f"https://text.pollinations.ai/{user_msg}?model={model}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"reply": response.text})
        return jsonify({"reply": "The void is currently closed."})
    except:
        return jsonify({"reply": "Connection lost to the abyss."})

# --- AUTH SYSTEM ---
@app.route('/api/auth/<action>', methods=['POST'])
def handle_auth(action):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    
    # Try connecting to the volume DB, fallback to local if it fails
    path = DB_PATH if os.path.exists(os.path.dirname(DB_PATH)) else 'users.db'
    conn = sqlite3.connect(path)
    
    if action == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?, ?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except: return jsonify({"error": "Identity already claimed."}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Rejected."}), 401)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
