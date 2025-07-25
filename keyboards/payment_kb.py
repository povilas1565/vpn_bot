from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from constants.tariffs import TARIFF_TITLES


def tariff_keyboard():
    buttons = [
        [InlineKeyboardButton(text=TARIFF_TITLES[key], callback_data=f"tariff_{key}")]
        for key in TARIFF_TITLES
    ]
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="cancel_payment")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def payment_keyboard(payment_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Перейти к оплате", url=payment_url)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="cancel_payment")]
        ]
    )

def topup_keyboard(payment_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Перейти к оплате", url=payment_url)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data="check_payment")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="cancel_payment")]
        ]
    )
def topup_amounts_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💵 100₽", callback_data="topup_100"),
                InlineKeyboardButton(text="💵 300₽", callback_data="topup_300"),
                InlineKeyboardButton(text="💵 500₽", callback_data="topup_500")
            ],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="cancel_payment")]
        ]
    )