from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from bot.messages.instructions import INSTRUCTIONS

router = Router()

PLATFORMS = ["Windows", "macOS", "iOS", "Android", "Linux"]

@router.message(lambda msg: msg.text == "📲 Инструкция" or msg.text == "/instruction")
async def instruction_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                            [InlineKeyboardButton(text=platform, callback_data=f"instr_{platform}")]
                            for platform in PLATFORMS
                        ] + [[InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]]
    )
    await message.answer("📲 Выберите вашу платформу:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("instr_"))
async def send_instruction(call: CallbackQuery):
    platform = call.data.split("_")[1]
    text = INSTRUCTIONS.get(platform, "Инструкция не найдена.")
    await call.message.edit_text(text)

@router.callback_query(lambda c: c.data == "main_menu")
async def go_to_main_menu(call: CallbackQuery):
    from handlers.common import menu  # импорт меню из common
    await call.message.answer("🏠 Главное меню", reply_markup=menu)