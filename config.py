import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "7859420249:AAHFIljsRCl809nu9DhhNzdNs62imfIBHOs")
ADMINS = list(map(int, os.getenv("ADMINS", "7223928350, 8471850445").split(',')))
PAYMENT_URL = os.getenv("PAYMENT_URL", "https://pay.freekassa.ru/")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:root@localhost:5432/vpn_db")
MERCHANT_ID = os.getenv("MERCHANT_ID", "koliks")
FREEKASSA_SECRET_KEY_1 = os.getenv("FREEKASSA_SECRET_KEY_1", "dPGRUs@xjSNd?iT")
FREEKASSA_SECRET_KEY_2 = os.getenv("FREEKASSA_SECRET_KEY_2", "=XaOJ4ginP@&8xZ")
# 🔑 JSON-строка с ключами от Veesp
VEESP_API_KEY = os.getenv("VEESP_API_KEY")
if VEESP_API_KEY:
    try:
        _parsed = json.loads(VEESP_API_KEY)
        VEESP_TOKEN = _parsed["token"]
        VEESP_REFRESH = _parsed["refresh"]
    except Exception:
        VEESP_TOKEN = VEESP_API_KEY  # fallback, если в .env лежит только строка
        VEESP_REFRESH = None
else:
    VEESP_TOKEN = None
    VEESP_REFRESH = None

