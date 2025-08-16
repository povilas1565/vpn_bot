import hashlib
import time

from config import MERCHANT_ID, PAYMENT_URL, FREEKASSA_SECRET_KEY_1


def generate_signature(order_id: str, amount: float) -> str:
    raw = f"{MERCHANT_ID}:{amount:.2f}:{order_id}:{FREEKASSA_SECRET_KEY_1}"
    return hashlib.md5(raw.encode()).hexdigest()


def create_payment_link(user_id: int, amount: float, tariff: str) -> str:
    order_id = f"{user_id}_{int(time.time())}"
    signature = generate_signature(order_id, amount)
    return (
        f"{PAYMENT_URL}?m={MERCHANT_ID}&oa={amount:.2f}&o={order_id}&s={signature}"
        f"&us_user_id={user_id}&us_tariff={tariff}"
    )
