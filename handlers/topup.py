from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.payment_kb import topup_keyboard, topup_amounts_keyboard  # добавь topup_amounts_keyboard
from services.payment import check_topup
from states.purchase import PurchaseState
from handlers.common import menu
from services.payment_link import create_payment_link

router = Router()

@router.message(F.text == "💰 Пополнить баланс")
async def topup_handler(message: Message, state: FSMContext):
    await state.set_state(PurchaseState.ChoosingTariff)
    await message.answer("💵 Выберите сумму пополнения:", reply_markup=topup_amounts_keyboard())

@router.callback_query(F.data.startswith("topup_"))
async def choose_topup_amount(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.split("_")[1])
    url = create_payment_link(callback.from_user.id, amount, tariff="topup")

    await state.set_state(PurchaseState.WaitingPayment)
    await state.update_data(payment_url=url, is_topup=True)

    await callback.message.edit_text(
        f"Вы выбрали пополнение на: <b>{amount}₽</b>\n"
        f"💳 Перейдите по ссылке для оплаты:",
        reply_markup=topup_keyboard(url)
    )

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