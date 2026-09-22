import hashlib
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.absolute()


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_URL: str

    WEBAPP_URL: str = ""
    VT_API_KEY: str = ""
    WHISPER_MODEL_SIZE: str = "base"
    DEFAULT_PREFIX: str = "."

    WEBHOOK_PATH: str = "/webhook"
    WEBHOOK_BASE_URL: str = ""
    WEBHOOK_SECRET: str = ""

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    CORS_ORIGINS_RAW: str = Field(default="", alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


def _derive_webhook_secret(bot_token: str) -> str:
    """Детерминированный secret_token для вебхука Telegram.

    Не храним ни в файле, ни в отдельной обязательной env-переменной —
    выводим из BOT_TOKEN, который и так есть. На эфемерной ФС (Render и
    подобные) это переживает рестарты/редеплои без ручной синхронизации
    секретов. Если BOT_TOKEN меняется — secret просто пересчитается и
    перерегистрируется на следующем старте (безопасно, в отличие от
    MIRROR_ENCRYPTION_KEY, см. core/crypto.py).
    """
    digest = hashlib.sha256(f"pomogator4business-webhook:{bot_token}".encode())
    return digest.hexdigest()


settings = Settings()

BOT_TOKEN = settings.BOT_TOKEN
DB_URL = settings.DB_URL

WEBAPP_URL = settings.WEBAPP_URL
VT_API_KEY = settings.VT_API_KEY
WHISPER_MODEL_SIZE = settings.WHISPER_MODEL_SIZE
DEFAULT_PREFIX = settings.DEFAULT_PREFIX

WEBHOOK_PATH = settings.WEBHOOK_PATH
WEBHOOK_BASE_URL = settings.WEBHOOK_BASE_URL
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}" if WEBHOOK_BASE_URL else None
WEBHOOK_SECRET = settings.WEBHOOK_SECRET or _derive_webhook_secret(BOT_TOKEN)

API_HOST = settings.API_HOST
API_PORT = settings.API_PORT

CORS_ORIGINS = [
    origin.strip() for origin in settings.CORS_ORIGINS_RAW.split(",") if origin.strip()
]

# --- Tortoise ORM / Aerich ---
TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": [
                "db.models.connection",
                "db.models.module_settings",
                "db.models.echo",
                "db.models.message_log",
                "db.models.mute",
                "db.models.story",
                "db.models.known_chat",
                "db.models.message_history",
                "db.models.archive_log",
                "db.models.profile_backup",
                "db.models.mirror_bot",
                "db.models.clock",
                "db.models.emoji_status",
                "db.models.user_locale",
                "db.models.voice_effect",
                "db.models.games",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}
