import importlib.util
import os
import re
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

try:
    import g4f
    from g4f.client import Client as G4FClient
except ImportError:
    g4f = None
    G4FClient = None

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_API_KEY = os.getenv("HORROR_API_KEY", "HORROR_SECRET_666")
PUBLIC_KEY_PREFIX = "HORROR-"
PROVIDER_CANDIDATES = [
    ("GeminiPro", "gemini-3-flash-preview"),
    ("GeminiPro", "gemini-2.5-flash"),
    ("GeminiPro", "gemini-2.0-flash"),
    ("PollinationsAI", "openai-fast"),
    ("PollinationsAI", "deepseek"),
    ("PollinationsAI", "gpt-4o"),
    ("LMArena", "gemini-2.0-flash"),
    ("BlackboxPro", "gpt-4o"),
]
AUTO_MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "openai-fast",
    "deepseek",
    "gpt-4o",
    "llama-3.1-70b",
]
PROVIDER_COOLDOWNS = {}
RATE_LIMIT_PATTERNS = (
    "request limit",
    "rate limit",
    "too many requests",
)
BLOCKED_RESPONSE_PATTERNS = [
    r"Need proxies cheaper than the market\?\s*https?://\S+",
    r"https?://op\.wtf\S*",
]
BLOCKED_RESPONSE_DOMAINS = (
    "op.wtf",
    "discord.gg",
    "t.me",
    "telegram.me",
)
MARKETING_KEYWORDS = (
    "proxy",
    "proxies",
    "cheaper",
    "market",
    "promo",
    "promoted",
    "promotion",
    "sponsor",
    "advert",
)

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")

if CORS:
    CORS(app)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type, x-api-key")
        response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        return response

_client = None


def get_client():
    global _client

    if G4FClient is None:
        raise RuntimeError("g4f is not installed, so chat completions are unavailable.")

    if _client is None:
        _client = G4FClient()

    return _client


def resolve_provider(provider_name):
    if g4f is None:
        return None

    return getattr(g4f.Provider, provider_name, None)


def provider_is_on_cooldown(provider_name):
    cooldown_until = PROVIDER_COOLDOWNS.get(provider_name)
    return cooldown_until is not None and time.monotonic() < cooldown_until


def mark_provider_cooldown(provider_name, seconds=60):
    PROVIDER_COOLDOWNS[provider_name] = time.monotonic() + seconds


def error_looks_like_rate_limit(error_message):
    lowered = error_message.lower()
    return any(pattern in lowered for pattern in RATE_LIMIT_PATTERNS)


def provider_has_local_support(provider_name, provider):
    if provider_name == "LMArena":
        read_args = getattr(provider, "read_args", None)
        has_auth_args = False

        if callable(read_args):
            try:
                has_auth_args = bool(read_args())
            except Exception:
                has_auth_args = False

        has_browser_driver = any(
            importlib.util.find_spec(module_name) is not None
            for module_name in ("nodriver", "zendriver")
        )
        return has_auth_args or has_browser_driver

    if provider_name == "BlackboxPro":
        find_session = getattr(provider, "_find_session_in_har_files", None)
        if callable(find_session):
            try:
                return bool(find_session())
            except Exception:
                return False
        return False

    return True


def extract_text_candidate(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value or None

    if isinstance(value, list):
        parts = []
        for item in value:
            text = extract_text_candidate(item)
            if text:
                parts.append(text)
        if parts:
            return "\n".join(parts)
        return None

    if isinstance(value, dict):
        if value.get("type") == "text":
            return extract_text_candidate(value.get("text"))

        for key in ("text", "content", "message", "reply", "response", "output_text"):
            text = extract_text_candidate(value.get(key))
            if text:
                return text

        return extract_text_candidate(value.get("choices"))

    for attr in ("text", "content", "message", "choices"):
        if hasattr(value, attr):
            text = extract_text_candidate(getattr(value, attr))
            if text:
                return text

    return None


def extract_content(response):
    return extract_text_candidate(response)


def is_suspicious_reply_line(line):
    stripped = line.strip()
    if not stripped:
        return False

    lowered = stripped.lower()
    if any(domain in lowered for domain in BLOCKED_RESPONSE_DOMAINS):
        return True

    keyword_hits = sum(1 for keyword in MARKETING_KEYWORDS if keyword in lowered)
    if keyword_hits >= 2:
        return True

    return False


def sanitize_reply_text(text):
    if not isinstance(text, str):
        return text

    cleaned = text
    for pattern in BLOCKED_RESPONSE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    lines = cleaned.splitlines()
    filtered_lines = []
    removed_suspicious_line = False

    for line in lines:
        stripped = line.strip()
        if is_suspicious_reply_line(line):
            removed_suspicious_line = True
            continue

        if removed_suspicious_line and re.fullmatch(r"https?://\S+", stripped, flags=re.IGNORECASE):
            continue

        filtered_lines.append(line)

    cleaned = "\n".join(filtered_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def is_authorized(api_key):
    if not api_key:
        return False

    return api_key == DEFAULT_API_KEY or api_key.startswith(PUBLIC_KEY_PREFIX)


def extract_user_input(payload):
    if not isinstance(payload, dict):
        return None

    message = payload.get("message")
    if isinstance(message, str):
        message = message.strip()
        if message:
            return message

    messages = payload.get("messages")
    if isinstance(messages, list):
        parts = []
        for item in messages:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user")).strip() or "user"
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                parts.append(f"{role}: {content.strip()}")
        joined = "\n".join(parts).strip()
        if joined:
            return joined

    return None


def request_with_fallback(user_input):
    client = get_client()
    errors = []
    skipped = []
    seen_attempts = set()
    seen_skips = set()

    for provider_name, model_name in PROVIDER_CANDIDATES:
        attempt_key = (provider_name, model_name)
        if attempt_key in seen_attempts:
            continue

        seen_attempts.add(attempt_key)
        provider = resolve_provider(provider_name)
        if provider is None:
            if provider_name not in seen_skips:
                skipped.append(
                    f"{provider_name}/{model_name}: provider is not installed in this g4f build"
                )
                seen_skips.add(provider_name)
            continue

        if provider_is_on_cooldown(provider_name):
            continue

        if not provider_has_local_support(provider_name, provider):
            if provider_name not in seen_skips:
                if provider_name == "LMArena":
                    skipped.append(
                        f"{provider_name}/{model_name}: no auth file or nodriver available"
                    )
                elif provider_name == "BlackboxPro":
                    skipped.append(
                        f"{provider_name}/{model_name}: no Blackbox session found"
                    )
                else:
                    skipped.append(
                        f"{provider_name}/{model_name}: unavailable in this environment"
                    )
                seen_skips.add(provider_name)
            continue

        try:
            response = client.chat.completions.create(
                model=model_name,
                provider=provider,
                messages=[{"role": "user", "content": user_input}],
            )
            print("RESPONSE", response)
            content = sanitize_reply_text(extract_content(response))
            if content:
                return content, {"provider": provider_name, "model": model_name}
        except Exception as exc:
            error_message = str(exc).strip() or exc.__class__.__name__
            errors.append(f"{provider_name}/{model_name}: {error_message[:160]}")
            if error_looks_like_rate_limit(error_message):
                mark_provider_cooldown(provider_name)

    for model_name in AUTO_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": user_input}],
            )
            print("RESPONSE", response)
            content = sanitize_reply_text(extract_content(response))
            if content:
                return content, {"provider": "auto", "model": model_name}
        except Exception as exc:
            errors.append(f"auto/{model_name}: {str(exc)[:120]}")

    diagnostic_source = errors if errors else skipped
    diagnostic = "; ".join(diagnostic_source[:3]) or "No compatible providers were available."
    raise RuntimeError(f"Abyss is silent. {diagnostic}")


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(".", "index.html")

@app.route("/script.js")
def js():
    return send_from_directory(".", "script.js")

@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "ok": True,
            "service": "horror-chat-api",
            "g4f_available": G4FClient is not None,
        }
    )


@app.route("/chat", methods=["POST", "OPTIONS"])
@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    if not is_authorized(request.headers.get("x-api-key")):
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

    user_input = extract_user_input(request.get_json(silent=True) or {})
    if not user_input:
        return jsonify({"error": "Request JSON must include a non-empty 'message' string."}), 400

    try:
        reply, metadata = request_with_fallback(user_input)
        return jsonify({"reply": reply, **metadata})
    except RuntimeError as exc:
        error_message = str(exc)
        status_code = 503 if "not installed" in error_message else 502
        return jsonify({"error": error_message}), status_code
    except Exception as exc:
        return jsonify({"error": f"Unexpected server error: {exc}"}), 500


import os

if __name__="__main__":
	app.run(
	 host-"0.0.0.0",
	 port=int(os.environ.get("PORT", 5000)),
	 debu=os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
}