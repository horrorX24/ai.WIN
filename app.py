import os
import random
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import resend # Make sure 'resend' is in your requirements.txt

# --- Configuration ---
# static_folder='.' tells Flask to look for script.js in the main folder
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Get API Key from Railway Variables
resend.api_key = os.getenv("RESEND_API_KEY")

# Temporary in-memory storage for OTPs
# (Note: This resets if Railway restarts the app)
otp_storage = {}

# --- Routes ---

# 1. THE HOME ROUTE (Fixes the 404 error)
@app.route('/')
def index():
    try:
        # This looks for index.html in your main directory
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Fatal Error: index.html not found in root directory.</h1>", 404

# 2. SERVE STATIC FILES (Ensures script.js is found)
@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('.', path)

# 3. REQUEST OTP
@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    if not resend.api_key:
        return jsonify({"error": "Email service not configured (Missing RESEND_API_KEY)"}), 500
    
    data = request.json
    email = data.get('email')
    
    if not email or "@" not in email:
        return jsonify({"error": "Invalid email"}), 400

    # Generate 6-digit code
    otp_code = str(random.randint(100000, 999999))
    otp_storage[email] = otp_code
    
    try:
        resend.Emails.send({
            "from": "Horror.ai <onboarding@resend.dev>",
            "to": [email],
            "subject": "Verification Code: " + otp_code,
            "html": f"""
                <div style="background:#000; color:#fff; padding:20px; text-align:center; border:1px solid #333;">
                    <h2 style="color:#a87ffb;">Horror.ai</h2>
                    <p>Enter this code to bind your identity:</p>
                    <h1 style="letter-spacing:5px; color:#a87ffb;">{otp_code}</h1>
                </div>
            """
        })
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. VERIFY OTP
@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    code = data.get('code')

    if email in otp_storage and otp_storage[email] == code:
        del otp_storage[email] # Code used, remove it
        return jsonify({
            "success": True, 
            "token": "GHOST-" + os.urandom(16).hex()
        }), 200
    
    return jsonify({"success": False, "message": "Invalid or expired code"}), 401

# --- Execution ---
if __name__ == '__main__':
    # Railway provides the PORT variable automatically
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
