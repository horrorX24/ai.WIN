import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# Path for the persistent volume
DB_PATH = '/app/data/users.db'

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

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')
    if len(password) < 3:
        return jsonify({"error": "Password too weak"}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Name already taken"}), 400

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
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
