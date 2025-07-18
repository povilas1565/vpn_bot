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

def check_topup(user_id: int) -> tuple[bool, float]:
    with SessionLocal() as session:
        payment = session.query(Payment).filter_by(
            user_id=user_id,
            status="confirmed",
            type="topup"
        ).order_by(Payment.date.desc()).first()

        if payment:
            return True, payment.amount
        return False, 0.0