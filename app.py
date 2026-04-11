import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import resend # pip install resend

app = Flask(__name__)
CORS(app)

# 1. Setup your Resend API Key (Get this from resend.com)
resend.api_key = os.getenv("RESEND_API_KEY")

# 2. Simple in-memory storage for codes (In production, use Redis or a DB)
otp_storage = {}

@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Generate 6-digit code
    otp_code = str(random.randint(100000, 999999))
    otp_storage[email] = otp_code
    
    # Send Email via Resend
    try:
        params = {
            "from": "Horror.ai <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your Access Code for the Void",
            "html": f"""
                <div style="background: #0f0f12; color: #e2e2e6; padding: 40px; font-family: sans-serif;">
                    <h1 style="color: #a87ffb;">Horror.ai</h1>
                    <p>The entity has acknowledged your request.</p>
                    <div style="background: #16161a; padding: 20px; border: 1px solid #2d2d35; border-radius: 12px; text-align: center;">
                        <span style="font-size: 32px; letter-spacing: 10px; font-weight: bold; color: #a87ffb;">{otp_code}</span>
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">If you did not request this, ignore the whispers.</p>
                </div>
            """
        }
        resend.Emails.send(params)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    code = data.get('code')

    if otp_storage.get(email) == code:
        # Clear the code after use
        del otp_storage[email]
        # In a real app, you'd return a JWT token here
        return jsonify({"success": True, "token": "VOICE-OF-THE-VOID-TOKEN"}), 200
    
    return jsonify({"success": False, "message": "Invalid code"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
