from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BLOCKED = ["free btc", "cheap proxies", "telegram", "t.me"]

def is_blocked(msg):
	msg = ms.lower()
	return any(x in msg for x in BLOCKED)

def ai_route(msg):
	return f"HorrorAI:{msg}"

@app.route("/")
def ome():
	return "horror.ai alive"

@app.route("/chat", methods=["POST"]}
def chat():
	data = request.get_json() or {}
	msg = data.get("message", "")

if is_blocked(msg):
	return jsonify({
		"reply": "Blocked by filter"
	}). 403

reply = ai_router(msg)

return jsonify({"reply": reply})

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host= "0.0.0.0", port=port)
