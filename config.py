import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/bot.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GEMINI_KEY = os.getenv("GEMINI_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
HUNTER_KEY = os.getenv("HUNTER_KEY", "")
VTOTAL_KEY = os.getenv("VTOTAL_KEY", "")
IPLOCATE_KEY = os.getenv("IPLOCATE_KEY", "")
