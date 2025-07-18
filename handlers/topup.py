from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import PAYMENT_URL
from keyboards.payment_kb import topup_keyboard
from services.payment import check_topup
from states.purchase import PurchaseState
from handlers.common import menu

router = Router()

@router.message(F.text == "💰 Пополнить баланс")
async def topup_handler(message: Message, state: FSMContext):
    await state.set_state(PurchaseState.WaitingPayment)
    url = f"{PAYMENT_URL}?topup=1&user={message.from_user.id}"
    await state.update_data(payment_url=url, is_topup=True)

    await message.answer("💵 Перейдите по ссылке для пополнения баланса:", reply_markup=topup_keyboard(url))

@router.callback_query(F.data == "check_payment")
async def check_topup_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    is_topup = data.get("is_topup", False)

    if is_topup:
        success, amount = check_topup(user_id)
        if not success:
            await callback.message.answer("❌ Пополнение пока не найдено.")
            return

        from database.db import SessionLocal
        from database.models import User

        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id, balance=amount)
                session.add(user)
            else:
                user.balance += amount
            session.commit()

        await callback.message.answer(f"✅ Баланс пополнен на {amount}₽!", reply_markup=menu)
        await state.clear()