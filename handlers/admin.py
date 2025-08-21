from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from config import ADMINS
from database.db import SessionLocal
from database.models import User

router = Router()


# Главное меню админа
def admin_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_list_users")],
        [InlineKeyboardButton(text="🛑 Заблокировать пользователя", callback_data="admin_ban_user")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="admin_exit")]
    ])
    return keyboard


# Команда /admin или кнопка
@router.message(F.from_user.id.in_(ADMINS), F.text == "/admin")
async def admin_start(message: Message):
    await message.answer("⚡ Админ-панель", reply_markup=admin_menu())


# Список пользователей
@router.callback_query(F.data == "admin_list_users")
async def list_users(call: CallbackQuery):
    with SessionLocal() as session:
        users = session.execute(User.__table__.select()).fetchall()
        if not users:
            text = "Нет пользователей."
        else:
            text = "\n".join([f"ID: {u.telegram_id}, до: {u.expire_date}" for u in users])
    await call.message.edit_text(f"👥 Пользователи:\n{text}", reply_markup=admin_menu())


# Блокировка пользователя — ввод ID
@router.callback_query(F.data == "admin_ban_user")
async def ban_user_start(call: CallbackQuery):
    await call.message.answer("❗ Отправьте ID пользователя для блокировки:")

    # Сохраняем состояние, чтобы следующий ответ был ID
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup

    class BanUserState(StatesGroup):
        waiting_for_id = State()

    state: FSMContext = router.bot.get('fsm_context')  # если FSMContext настроен глобально
    await state.set_state(BanUserState.waiting_for_id)


# Обработка ID пользователя для блокировки
@router.message(F.from_user.id.in_(ADMINS))
async def ban_user_process(message: Message, state):
    data = await state.get_state()
    if not data:
        return  # мы не в состоянии ожидания ID

    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Неверный ID, попробуйте ещё раз.")
        return

    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден")
        else:
            user.status = "expired"
            session.commit()
            await message.answer(f"✅ Пользователь {user_id} заблокирован", reply_markup=admin_menu())

    await state.clear()
