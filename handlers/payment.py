from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from anyio.to_thread import run_sync

from core.wg.provisioner import create_vpn_access
from keyboards.payment_kb import payment_keyboard, tariff_keyboard
from services.payment import check_payments, get_user_payments
from services.payment_link import create_payment_link
from states.purchase import PurchaseState
from handlers.common import menu
from constants.tariffs import TARIFF_PRICES, TARIFF_TITLES

router = Router()

@router.message(lambda msg: msg.text == "💳 Оплата")
async def start_payment(message: Message, state: FSMContext):
    await state.set_state(PurchaseState.ChoosingTariff)
    await message.answer("💰 Выберите тариф:", reply_markup=tariff_keyboard())

@router.callback_query(F.data.startswith("tariff_"))
async def choose_tariff(callback: CallbackQuery, state: FSMContext):
    tariff = callback.data.split("_")[1]

    amount = TARIFF_PRICES.get(tariff)
    if amount is None:
        await callback.message.answer("⚠️ Неизвестный тариф.")
        return

    pay_url = create_payment_link(callback.from_user.id, amount, tariff)
    await state.set_state(PurchaseState.WaitingPayment)
    await state.update_data(tariff=tariff, payment_url=pay_url)

    await callback.message.edit_text(
        f"Вы выбрали тариф: <b>{TARIFF_TITLES[tariff]}</b>\n"
        f"💸 Сумма: {amount:.2f}₽\n"
        f"Перейдите по ссылке для оплаты:",
        reply_markup=payment_keyboard(pay_url)
    )

@router.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    tariff = data.get("tariff")

    # Здесь нужно, чтобы check_payments возвращала статус (str), а не bool
    payment_status = await run_sync(check_payments, user_id, tariff)

    if payment_status == "pending":
        await callback.message.answer("⏳ Платеж в обработке. Пожалуйста, подождите и проверьте позже.")
        return
    elif payment_status != "confirmed":
        await callback.message.answer("❌ Оплата пока не найдена или отклонена.")
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
    await callback.message.answer("🏠 Вы возвращены в главное меню", reply_markup=menu)
    await state.clear()

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Покупка отменена.", reply_markup=menu)

@router.message(F.text == "📜 История платежей")
async def show_history(message: Message):
    payments = await run_sync(get_user_payments, message.from_user.id)

    if not payments:
        await message.answer("💤 У вас пока нет ни одного платежа.")
        return

    lines = []
    for p in payments[:10]:
        dt = p.created_at.strftime("%d.%m.%Y %H:%M")
        lines.append(f"📅 {dt} | 💳 {p.type} | 💰 {p.amount}₽ | Статус: {p.status}")

    await message.answer("📜 История платежей:\n\n" + "\n".join(lines))