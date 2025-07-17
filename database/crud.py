from sqlalchemy import select

from database.db import SessionLocal
from database.models import User


async def get_user_by_telegram_id(telegram_id: int):
    async with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def create_user(telegram_id: int, expire_date, server_id: int):
    async with SessionLocal() as session:
        user = User(
            telegram_id=telegram_id,
            expire_date=expire_date,
            server_id=server_id
        )
        session.add(user)
        await session.commit()
        return user