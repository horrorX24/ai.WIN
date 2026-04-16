import os
import sqlite3
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# --- DATABASE PATH LOGIC ---
# If Railway Volume is mounted at /app/data, use it. Otherwise, use a local file.
# This prevents the app from crashing during the first deployment.
if os.path.exists('/app/data'):
    DB_PATH = '/app/data/users.db'
else:
    DB_PATH = 'users.db'

def init_db():
    try:
        # Create folder if it's missing (only for volume paths)
        if os.path.dirname(DB_PATH):
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT)')
        conn.commit()
        conn.close()
        print(f"[*] Database initialized successfully at: {DB_PATH}")
    except Exception as e:
        print(f"[!] Database initialization failed: {e}")

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    # Serves your index.html from the root folder
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '')
    
    # Try multiple free models in order of stability
    # If Gemini fails, it moves to OpenAI, then Llama
    models = ["gemini", "openai", "llama-3-70b", "mistral-7b"]
    
    for model in models:
        try:
            # 8-second timeout to catch "Bad Gateways" quickly
            url = f"https://text.pollinations.ai/{user_msg}?model={model}&cache=true"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200 and response.text.strip():
                return jsonify({"reply": response.text})
        except:
            continue # Try the next model
            
    return jsonify({"reply": "The abyss is currently overwhelmed. Please try your incantation again."}), 503

@app.route('/api/auth/<action>', methods=['POST'])
def handle_auth(action):
    data = request.json
    u = data.get('username', '').lower().strip()
    p = data.get('password', '').strip()
    
    if not u or not p:
        return jsonify({"error": "Credentials required"}), 400

    conn = sqlite3.connect(DB_PATH)
    
    if action == 'signup':
        try:
            conn.execute('INSERT INTO users VALUES (?, ?)', (u, p))
            conn.commit()
            return jsonify({"success": True})
        except sqlite3.IntegrityError:
            return jsonify({"error": "Identity already claimed."}), 400
        finally:
            conn.close()
    else:
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p)).fetchone()
        conn.close()
        return jsonify({"success": True}) if user else (jsonify({"error": "Rejected."}), 401)

# --- ADMIN SECRETS ---
@app.route('/the-void-secrets')
def admin_view():
    # Access this via: your-url.com/the-void-secrets?key=my-secret-key-123
    key = request.args.get('key')
    if key != "my-secret-key-123":
        return "The void remains closed to you.", 403
    
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return {"registered_souls": users}

if __name__ == '__main__':
    # Railway provides the PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
