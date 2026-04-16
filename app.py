import os
import random
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.')

otp_storage = {}
EMAIL_SENDER = "horrorxxy@gmail.com" 
EMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD") 

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/otp/request', methods=['POST'])
def request_otp():
    email = request.json.get('email')
    otp_code = str(random.randint(100000, 999999))
    otp_storage[email] = otp_code

    try:
        msg = EmailMessage()
        msg.set_content(f"Your Horror.ai access code is: {otp_code}")
        msg['Subject'] = 'Horror.ai Access Code'
        msg['From'] = f"Horror.ai <{EMAIL_SENDER}>"
        msg['To'] = email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/otp/verify', methods=['POST'])
def verify_otp():
    data = request.json
    if otp_storage.get(data['email']) == data['code']:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
