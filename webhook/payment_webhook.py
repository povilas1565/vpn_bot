import datetime

from fastapi import FastAPI, Request
from database.db import SessionLocal
from database.models import Payment

app = FastAPI()

@app.post("/payment/callback")
async def payment_callback(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    tariff = data.get("tariff")
    payment_id = data.get("payment_id")
    status = data.get("status")

    if not all([user_id, tariff, status]):
        return {"error": "Missing fields"}

    async with SessionLocal() as session:
        payment = Payment(
            user_id=user_id,
            type=tariff,
            id=payment_id,
            status=status,
            created_at=datetime.datetime.utcnow()
        )
        session.add(payment)
        await session.commit()

    return {"status": "ok"}