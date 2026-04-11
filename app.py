import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

@app.route('/')
def index():
    # This serves your index.html from the root folder
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    return jsonify({"reply": "The void is listening."})

@app.route('/api/otp/request', methods=['POST'])
def otp_req():
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
