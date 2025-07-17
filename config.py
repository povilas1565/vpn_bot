import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "7859420249:AAHFIljsRCl809nu9DhhNzdNs62imfIBHOs")
ADMINS = list(map(int, os.getenv("ADMINS", "123456789,987654321").split(',')))
PAYMENT_URL = os.getenv("PAYMENT_URL", "https://your-payment-page.com/")
DB_URL = os.getenv("DB_URL", "postgresql://postgres:root@localhost:5432/vpn_db")