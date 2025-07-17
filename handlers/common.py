from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from database.db import SessionLocal
from database.models import User

router = Router()

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Оплата")],
        [KeyboardButton(text="📲 Инструкция")],
        [KeyboardButton(text="👤 Мой аккаунт")],
        [KeyboardButton(text="🆘 Поддержка")],
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)

@router.message(lambda msg: msg.text == "/start" or msg.text == "🏠 Главное меню")
async def start(message: Message):
    await message.answer("Добро пожаловать!", reply_markup=menu)

@router.message(lambda msg: msg.text == "👤 Мой аккаунт")
async def my_account(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            User.__table__.select().where(User.telegram_id == message.from_user.id)
        )
        user = result.first()
        if not user:
            await message.answer("🙁 У вас пока нет активной подписки.")
        else:
            u = user[0]
            await message.answer(
                f"👤 Ваш аккаунт:\n"
                f"🆔 ID: {u.telegram_id}\n"
                f"⏳ Подписка до: {u.expire_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"🖥 Сервер: {u.server_id}"
            )

@router.message(lambda msg: msg.text == "🆘 Поддержка")
async def support(message: Message):
    await message.answer("📞 Напишите нашему администратору: @YourAdminUsername")

@router.message(lambda msg: msg.text == "🏠 Главное меню")
async def main_menu(message: Message):
    await message.answer("Вы вернулись в главное меню:", reply_markup=menu)