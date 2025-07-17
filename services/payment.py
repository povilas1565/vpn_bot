from database.db import SessionLocal
from database.models import Payment

def check_payments(user_id: int, tariff: str):
    with SessionLocal() as session:
        result = session.execute(
            Payment.__table__.select().where(
                Payment.user_id == user_id,
                Payment.status == "confirmed",
                Payment.type == tariff
            )
        )
        return result.first() is not None