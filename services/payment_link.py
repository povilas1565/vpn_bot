import hashlib
import time

MERCHANT_ID = "koliks"
SECRET_KEY_1 = "dPGRUs@xjSNd?iT"
BASE_URL = "https://pay.freekassa.ru/"

def generate_signature(order_id: str, amount: float) -> str:
    raw = f"{MERCHANT_ID}:{amount:.2f}:{order_id}:{SECRET_KEY_1}"
    return hashlib.md5(raw.encode()).hexdigest()

def create_payment_link(user_id: int, amount: float, tariff: str) -> str:
    order_id = f"{user_id}_{int(time.time())}"
    signature = generate_signature(order_id, amount)
    return (
        f"{BASE_URL}?m={MERCHANT_ID}&oa={amount:.2f}&o={order_id}&s={signature}"
        f"&us_user_id={user_id}&us_tariff={tariff}"
    )