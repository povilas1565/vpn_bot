from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def tariff_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Base (40 юзеров)", callback_data="tariff_base")],
            [InlineKeyboardButton(text="⚡ Silver (20 юзеров)", callback_data="tariff_silver")],
            [InlineKeyboardButton(text="👑 Gold (3 юзера)", callback_data="tariff_gold")]
        ]
    )

def payment_keyboard(payment_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Перейти к оплате", url=payment_url)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
        ]
    )