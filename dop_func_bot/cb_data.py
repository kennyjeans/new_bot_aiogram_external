from aiogram.filters.callback_data import CallbackData


# CallBackData для подтверждения или отказа
class AcceptBuy(CallbackData, prefix='accept_buy'):
    user_id: int
    order_id: int


class CancelBuy(CallbackData, prefix='cancel_buy'):
    user_id: int
    order_id: int
