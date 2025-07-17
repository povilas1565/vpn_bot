from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from config import PAYMENT_URL
from core.wg.provisioner import create_vpn_access
from keyboards.payment_kb import payment_keyboard, tariff_keyboard
from services.payment import check_payments
from states.purchase import PurchaseState

router = Router()

# Старт покупки
@router.message(lambda msg: msg.text.lower() == "💳 Оплата")
async def start_payment(message: Message, state: FSMContext):
    await state.set_state(PurchaseState.ChoosingTariff)
    await message.answer("💰 Выберите тариф:", reply_markup=tariff_keyboard())

# Выбор тарифа
@router.callback_query(F.data.startswith("tariff_"))
async def choose_tariff(callback: CallbackQuery, state: FSMContext):
    tariff = callback.data.split("_")[1]
    
    pay_url = f"{PAYMENT_URL}?tariff={tariff}&user={callback.from_user.id}"
    await state.set_state(PurchaseState.WaitingPayment)
    await state.update_data(tariff=tariff, payment_url=pay_url)

    await callback.message.edit_text(
        f"Вы выбрали тариф: <b>{tariff.capitalize()}</b>\n"
        "Перейдите по ссылке для оплаты:",
        reply_markup=payment_keyboard(pay_url)
    )

@router.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    tariff = data.get("tariff")

    payment_confirmed = await check_payments(user_id, tariff)

    if not payment_confirmed:
        await callback.message.answer("❌ Оплата пока не найдена.")
        return

    await callback.message.edit_text("✅ Оплата подтверждена! Генерирую VPN-доступ...")

    result, error = await create_vpn_access(user_id, tariff)

    if error:
        await callback.message.answer(error)
        return

    conf_path, qr_path = result
    await callback.message.answer("📦 Ваш VPN доступ готов!")

    await callback.message.answer_photo(FSInputFile(qr_path), caption="🔐 QR-код для подключения")
    await callback.message.answer_document(FSInputFile(conf_path), caption="📄 Конфигурационный файл")
    await state.clear()
    
# Отмена
@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Покупка отменена.")