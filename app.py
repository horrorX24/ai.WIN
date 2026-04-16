import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# --- PERMANENT STORAGE CONFIG ---
# This points to the Volume you attached to /app/data
DB_PATH = '/app/data/users.db'
SECRET_ADMIN_KEY = "my-secret-key-123" # Access via: /the-void-secrets?key=my-secret-key-123

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# ADMIN PANEL: Only horrorxxy@gmail.com should know this URL
@app.route('/the-void-secrets')
def admin_view():
    user_key = request.args.get('key')
    if user_key != SECRET_ADMIN_KEY:
        return "The void remains closed to you.", 403
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users')
    all_users = cursor.fetchall()
    conn.close()
    
    html = "<body style='background:#000;color:#a87ffb;font-family:monospace;padding:50px;'>"
    html += "<h1>SECURED USER ARCHIVE</h1><hr>"
    for user in all_users:
        html += f"<p>> USERNAME: {user[0]} | PASSWORD: {user[1]}</p>"
    return html

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')

    if len(password) < 3:
        return jsonify({"error": "Password too weak (min 3 chars)"}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "That name is already claimed."}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True})
    return jsonify({"error": "Credentials rejected."}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
