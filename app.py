import os
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import resend

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

# Railway Environment Variable
resend.api_key = os.getenv("RESEND_API_KEY")

# Temporary store for OTP codes
otp_storage = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    data = request.json
    contact = data.get('contact')
    country_code = data.get('countryCode', '') # e.g., "+91"
    
    if not contact:
        return jsonify({"error": "Information required"}), 400

    otp_code = str(random.randint(100000, 999999))
    
    # If it's an email
    if "@" in contact:
        target = contact
        otp_storage[target] = otp_code
        try:
            resend.Emails.send({
                "from": "Horror.ai <onboarding@resend.dev>",
                "to": [target],
                "subject": f"Your Access Code: {otp_code}",
                "html": f"<div style='background:#000;color:#a87ffb;padding:20px;'><h1>{otp_code}</h1></div>"
            })
            return jsonify({"success": True, "type": "email"})
        except Exception as e:
            return jsonify({"error": "Mail failed to send"}), 500
    
    # If it's a phone number
    else:
        # Remove any leading zeros the user might have typed
        clean_phone = contact.lstrip('0')
        full_phone = f"{country_code}{clean_phone}"
        otp_storage[full_phone] = otp_code
        
        # DEBUG: In a real app, use Twilio here. For now, we log it.
        print(f"--- OTP SENT TO {full_phone}: {otp_code} ---")
        return jsonify({"success": True, "type": "phone", "target": full_phone})

@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    target = data.get('target') # The full email or full phone (+91...)
    code = data.get('code')

    if otp_storage.get(target) == code:
        del otp_storage[target]
        return jsonify({"success": True, "token": "SECURE_VOID_TOKEN"})
    
    return jsonify({"success": False, "message": "Invalid code"}), 401

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '')
    return jsonify({"reply": f"The void echoes: {msg}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
