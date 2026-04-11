from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def gemini_pro(msg):
	return f"[GeminiPro] {msg}"

def pollinations_ai(msg):
	return f"[pollinations] {msg}"

def lmarena(msg):
	return f"[LMArena] {msg}"

def blackboxpro(msg):
	return f"[BlackboxPro] {msg}"

def choose_provider(msg):
	msg = msg.lower()

if "fast" in ms:
	return "pollinations"
elif "smart" in msg:
	return "gemini"
elif "code" in msg:
	return "blackbox"
else:
	return"lmarena"

def run_ai(msg):
	provider = choose_provider(msg)

if provider == "gemini"
return gemini_pro(msg)
elif provider == "pollinations":
return pollinations_ai(msg)
elif provider == "blackbox"
return blackboxpro(msg)
else:
	return lmarena(msg)

@app.route("/")
def home():
	return "horror.ai multi-brain system"

@app.route("/chat", methods=["POST'])
							 def chat():
							 data = request.get_json() or {}
							 msg = data.get("message", "")

							 reply = run_ai(msg

							 return jsonify({"reply":reply})

							 if __name__ =="__main__"
							 import os
							 port = int(os.environ.get("PORT", 5000))
							 app.run(host="0.0.0.0", port=port)
