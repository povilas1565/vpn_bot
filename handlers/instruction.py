from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from bot.messages.instructions import INSTRUCTIONS

router = Router()

PLATFORMS = ["Windows", "macOS", "iOS", "Android", "Linux"]

@router.message(lambda msg: msg.text.lower() == "instruction" or msg.text == "/instruction")
async def instruction_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=platform, callback_data=f"instr_{platform}")]
            for platform in PLATFORMS
        ]
    )
    await message.answer("📲 Выберите вашу платформу:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("instr_"))
async def send_instruction(call: CallbackQuery):
    platform = call.data.split("_")[1]
    text = INSTRUCTIONS.get(platform, "Инструкция не найдена.")
    await call.message.edit_text(text)