import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# --- DATABASE PATH (Ensure this matches your Volume Mount) ---
DB_PATH = '/app/data/users.db'
ADMIN_KEY = "my-secret-key-123"

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

# --- THE SECRET VIEW ---
@app.route('/the-void-secrets')
def admin_view():
    key = request.args.get('key')
    if key != ADMIN_KEY:
        return "Forbidden", 403
    
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return {"database_content": users}

# --- AI CHAT (Using Free Pollinations Provider) ---
@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    try:
        # Free provider: Pollinations
        ai_url = f"https://text.pollinations.ai/{user_msg}?model=openai&system=You are Horror.ai, a helpful but mysterious AI."
        response = requests.get(ai_url)
        return jsonify({"reply": response.text})
    except:
        return jsonify({"reply": "The void is currently unreachable."})

# --- LOGIN/SIGNUP ---
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
        except:
            return jsonify({"error": "User exists"}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Wrong login"}), 401)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
