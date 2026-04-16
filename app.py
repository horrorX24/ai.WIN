import os
import random
import resend # Ensure 'resend' is in your requirements.txt
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

# Set this in your Railway Variables
resend.api_key = os.environ.get("RESEND_API_KEY")

# In-memory store (Codes reset if server restarts)
otp_storage = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    email = request.json.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Generate 6-digit code
    otp_code = str(random.randint(100000, 999999))
    otp_storage[email] = otp_code
    
    try:
        # Sending via Resend
        resend.Emails.send({
            "from": "Void <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your Horror.ai Access Code",
            "html": f"""
                <div style="background:#0f0f12; color:#fff; padding:20px; font-family:sans-serif; text-align:center; border-radius:10px;">
                    <h2 style="color:#a87ffb;">Horror.ai</h2>
                    <p>Your 6-digit access code is:</p>
                    <h1 style="letter-spacing:10px; font-size:40px;">{otp_code}</h1>
                </div>
            """
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    
    if otp_storage.get(email) == code:
        del otp_storage[email] # Clear code after successful use
        return jsonify({"success": True})
    
    return jsonify({"success": False}), 401

if __name__ == '__main__':
    # Railway listens on 0.0.0.0 and a dynamic port
    port = int(os.environ.get('PORT', 8080)) 
    app.run(host='0.0.0.0', port=port)
