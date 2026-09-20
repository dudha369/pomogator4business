import os
import secrets

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в .env")

DB_PATH = os.getenv("DB_PATH", "bot.db")
DEFAULT_PREFIX = "."
VT_API_KEY = os.getenv("VT_API_KEY")

WEBAPP_URL = os.getenv("WEBAPP_URL")
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}" if WEBHOOK_BASE_URL else None

_SECRET_FILE = "webhook.secret"


def _load_webhook_secret():
    env_secret = os.getenv("WEBHOOK_SECRET")
    if env_secret:
        return env_secret
    if os.path.exists(_SECRET_FILE):
        with open(_SECRET_FILE, "r") as f:
            return f.read().strip()
    secret = secrets.token_urlsafe(32)
    with open(_SECRET_FILE, "w") as f:
        f.write(secret)
    return secret


WEBHOOK_SECRET = _load_webhook_secret()

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
