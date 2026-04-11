import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# The static_folder='.' is vital so Flask serves your JS/HTML from the root
app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app) # This allows the frontend to talk to the backend

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# This is the route your JS is looking for
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        persona = data.get('persona', 'You are a dark entity.')
        
        # FOR NOW: Returning a mock response to prove connection works
        # Later, you will plug your Gemini/OpenAI logic here
        return jsonify({"reply": f"The void heard: '{user_message}'. Your persona is: {persona}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
