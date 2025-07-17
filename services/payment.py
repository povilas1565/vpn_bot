from database.db import SessionLocal
from database.models import Payment

async def check_payments(user_id: int, tariff: str):
    async with SessionLocal() as session:
        result = await session.execute(
            Payment.__table__.select().where(
                Payment.user_id == user_id,
                Payment.status == "confirmed",
                Payment.type == tariff
            )
        )
        return result.first() is not None
