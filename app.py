import os
import random
import resend # Ensure 'resend' is in requirements.txt
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')
resend.api_key = os.environ.get("RESEND_API_KEY")

otp_storage = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    email = request.json.get('email')
    otp_code = str(random.randint(100000, 999999))
    otp_storage[email] = otp_code
    
    try:
        resend.Emails.send({
            "from": "Horror.ai <onboarding@resend.dev>",
            "to": [email],
            "subject": "Your Access Code",
            "html": f"<strong>Your 6-digit code is: {otp_code}</strong>"
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    if otp_storage.get(data['email']) == data['code']:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401
