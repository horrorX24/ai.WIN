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
    try:
        # Use Pollinations with a timeout to prevent hanging on provider errors
        res = requests.get(f"https://text.pollinations.ai/{user_msg}?model=gemini", timeout=12)
        if res.status_code == 200:
            return jsonify({"reply": res.text})
        return jsonify({"reply": "The void is busy. Try again."}), 502
    except:
        return jsonify({"reply": "The connection to the abyss was lost."}), 500

@app.route('/api/auth/<action>', methods=['POST'])
def auth(action):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    conn = sqlite3.connect(DB_PATH)
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
