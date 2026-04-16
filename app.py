import os
import random
import resend  # Make sure to run: pip install resend
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

# Replace with your actual key from resend.com in Railway Variables
resend.api_key = os.environ.get("RESEND_API_KEY")

# Temporary in-memory storage for OTP codes
otp_store = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    data = request.json
    target = data.get('contact')
    
    if not target or "@" not in target:
        return jsonify({"error": "Invalid Gmail address"}), 400

    otp_code = str(random.randint(100000, 999999))
    otp_store[target] = otp_code
    
    try:
        # Sending via Resend
        resend.Emails.send({
            "from": "Horror.ai <onboarding@resend.dev>",
            "to": [target],
            "subject": "Your Access Code",
            "html": f"""
                <div style="font-family: sans-serif; background: #0f0f12; color: #fff; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #a87ffb;">Horror.ai</h2>
                    <p>The void has generated your access code:</p>
                    <h1 style="letter-spacing: 5px; color: #a87ffb;">{otp_code}</h1>
                    <p style="font-size: 12px; color: #555;">If you didn't request this, ignore the whispers.</p>
                </div>
            """
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    target = data.get('target')
    code = data.get('code')
    
    if otp_store.get(target) == code:
        # Clear code after successful use
        del otp_store[target]
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "The code is incorrect."}), 401

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    return jsonify({"reply": f"The void echoes: {msg}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
