from aiogram import Router, F
from aiogram.types import Message
from database.db import SessionLocal
from database.models import User

router = Router()
ADMINS = [123456789]  # замени на свой Telegram ID

@router.message(F.from_user.id.in_(ADMINS), F.text == "/users")
async def list_users(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(User.__table__.select())
        users = result.fetchall()
        text = "\n".join([f"ID: {u[0].telegram_id}, до: {u[0].expire_date}" for u in users])
        await message.answer(f"👥 Пользователи:\n{text or 'Нет пользователей.'}")

@router.message(F.from_user.id.in_(ADMINS), F.text.startswith("/ban"))
async def ban_user(message: Message):
    try:
        user_id = int(message.text.split()[1])
    except:
        await message.answer("❗ Формат: /ban <user_id>")
        return

    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        user.status = "expired"
        await session.commit()
        await message.answer("✅ Пользователь заблокирован")