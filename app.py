import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
DB_PATH = '/app/data/users.db'

def init_db():
    try:
        # Create directory only if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Initialization Error: {e}")

init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message')
    # Supports 'gemini' or 'openai' (Horror)
    chosen_model = data.get('model', 'gemini') 
    
    try:
        # Using Pollinations as the free provider for both models
        api_url = f"https://text.pollinations.ai/{user_msg}?model={chosen_model}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"reply": response.text})
        return jsonify({"reply": "The void is silent. (Provider Error)"})
    except Exception as e:
        return jsonify({"reply": f"The void encountered an error: {str(e)}"}), 500

@app.route('/api/auth/<action>', methods=['POST'])
def handle_auth(action):
    data = request.json
    u, p = data.get('username', '').lower(), data.get('password', '')
    
    # Check if volume exists, otherwise use local fallback to prevent crash
    db_to_use = DB_PATH if os.path.exists('/app/data') else 'users.db'
    conn = sqlite3.connect(db_to_use)
    
    if action == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?, ?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except:
            return jsonify({"error": "Identity already taken."}), 400
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        return jsonify({"success": True}) if user else (jsonify({"error": "Access Denied."}), 401)

# Secret Admin Route
@app.route('/the-void-secrets')
def admin_view():
    if request.args.get('key') != "my-secret-key-123":
        return "Forbidden", 403
    db_to_use = DB_PATH if os.path.exists('/app/data') else 'users.db'
    conn = sqlite3.connect(db_to_use)
    users = conn.execute('SELECT * FROM users').fetchall()
    return {"users": users}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
