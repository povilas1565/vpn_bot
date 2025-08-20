from aiogram.fsm.state import StatesGroup, State


class PurchaseState(StatesGroup):
    ChoosingTariff = State()
    WaitingPayment = State()
