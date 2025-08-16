import datetime
import logging

from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse

from config import FREEKASSA_SECRET_KEY_2
from database.db import SessionLocal
from database.models import Payment, User
import hashlib

app = FastAPI()

logging.basicConfig(level=logging.INFO)


def verify_signature(m: str, oa: str, o: str, s: str) -> bool:
    sign_str = f"{m}:{oa}:{o}:{FREEKASSA_SECRET_KEY_2}"
    expected = hashlib.md5(sign_str.encode()).hexdigest()
    return expected == s


@app.post("/payment/callback")
async def payment_callback(
        m: str = Form(...),
        oa: str = Form(...),
        o: str = Form(...),
        s: str = Form(...),
        us_user_id: int = Form(...),
        us_tariff: str = Form(...),
):
    if not verify_signature(m, oa, o, s):
        return JSONResponse(content={"error": "invalid signature"}, status_code=403)

    try:
        amount = float(oa)
        status = "confirmed"

        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == us_user_id).first()
            if not user:
                user = User(telegram_id=us_user_id, balance=0)
                session.add(user)
                session.flush()

            # Пополнение баланса
            if us_tariff == "topup":
                user.balance += amount

            # Запись в таблицу платежей
            payment = Payment(
                id=o,
                user_id=user.id,
                type=us_tariff,
                amount=amount,
                status=status,
                created_at=datetime.datetime.utcnow()
            )
            session.add(payment)
            logging.info(
                f"💰 Payment received: user_id={us_user_id}, tariff={us_tariff}, amount={amount}, order_id={o}")
            session.commit()

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
