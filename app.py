import os
import sqlite3
import g4f # New Sandbox Engine
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
DB_PATH = '/app/data/users.db' if os.path.exists('/app/data') else 'users.db'

def init_db():
    if os.path.dirname(DB_PATH): os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    model_name = data.get('model', 'gpt-4o') # Default to 4o
    
    try:
        # G4F routes your request to the best working free provider automatically
        response = g4f.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": msg}],
        )
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"reply": f"Sandbox Error: {str(e)}"}), 500

# --- MODIFIED AUTH: LOGIN ONLY ---
@app.route('/api/auth/<action>', methods=['POST'])
def auth(action):
    if action == 'signup':
        # This disables new registrations
        return jsonify({"error": "Registration is closed by admin."}), 403
    
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    
    conn = sqlite3.connect(DB_PATH)
    user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
    conn.close()
    
    if user:
        return jsonify({"success": True})
    return jsonify({"error": "Invalid credentials."}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
