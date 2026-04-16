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

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message')
    
    # List of models to try if the first one fails
    models = ["gemini", "openai", "mistral", "llama"]
    
    for model in models:
        try:
            # Adding a 5-second timeout so it switches fast if a model is slow
            url = f"https://text.pollinations.ai/{user_msg}?model={model}&cache=false"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200 and res.text.strip():
                return jsonify({"reply": res.text})
        except:
            continue # Try the next model in the list
            
    return jsonify({"reply": "The abyss is currently full. Try again in a moment."}), 503

@app.route('/api/auth/<action>', methods=['POST'])
def auth(action):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    # Fallback to local DB if Volume isn't mounted yet
    path = DB_PATH if os.path.exists('/app/data') else 'users.db'
    conn = sqlite3.connect(path)
    if action == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?,?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except: return jsonify({"error": "Taken"}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u,p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Fail"}), 401)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
