import os
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# vital: '.' tells Flask everything is in the root folder
app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    return jsonify({"reply": f"The void echoes: {data.get('message')}"})

@app.route('/api/otp/request', methods=['POST'])
def otp_req():
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
