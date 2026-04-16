import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
DB_PATH = '/app/data/users.db'

def init_db():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Volume error: {e}")

init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message')
    # Supporting Arena/Gemini via model parameter
    model = data.get('model', 'openai') 
    
    try:
        url = f"https://text.pollinations.ai/{user_msg}?model={model}"
        response = requests.get(url, timeout=10)
        return jsonify({"reply": response.text})
    except:
        return jsonify({"reply": "The void is silent."})

@app.route('/api/auth/<action>', methods=['POST'])
def auth(action):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    conn = sqlite3.connect(DB_PATH if os.path.exists('/app/data') else 'users.db')
    if action == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?,?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except: return jsonify({"error": "Taken"}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Fail"}), 401)

# Secret Admin View
@app.route('/the-void-secrets')
def admin():
    if request.args.get('key') == "my-secret-key-123":
        conn = sqlite3.connect(DB_PATH if os.path.exists('/app/data') else 'users.db')
        res = conn.execute('SELECT * FROM users').fetchall()
        return {"users": res}
    return "Forbidden", 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
