import datetime

from database.db import SessionLocal
from database.models import Payment

def check_payments(user_id: int, tariff: str) -> str:
    with SessionLocal() as session:
        payment = session.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.type == tariff
        ).order_by(Payment.created_at.desc()).first()

        if not payment:
            return "not_found"
        return payment.status

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

def delete_old_unconfirmed_payments(days: int = 1):
    threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    with SessionLocal() as session:
        deleted = session.query(Payment).filter(
            Payment.status != "confirmed",
            Payment.created_at < threshold
        ).delete()
        session.commit()
    return deleted

def get_user_payments(user_id: int):
    with SessionLocal() as session:
        return session.query(Payment).filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()