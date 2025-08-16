import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "7859420249:AAHFIljsRCl809nu9DhhNzdNs62imfIBHOs")
ADMINS = list(map(int, os.getenv("ADMINS", "123456789,987654321").split(',')))
PAYMENT_URL = os.getenv("PAYMENT_URL", "https://pay.freekassa.ru/")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:root@localhost:5432/vpn_db")
MERCHANT_ID = os.getenv("MERCHANT_ID", "koliks")
FREEKASSA_SECRET_KEY_1 = os.getenv("FREEKASSA_SECRET_KEY_1", "dPGRUs@xjSNd?iT")
FREEKASSA_SECRET_KEY_2 = os.getenv("FREEKASSA_SECRET_KEY_2", "=XaOJ4ginP@&8xZ")