from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dop_func_bot.cb_data import AcceptBuy, CancelBuy

def start_kb():
    ikb = [[InlineKeyboardButton(text="MP-KESHBEK",
                                 url="https://mp-keshbek.ru/")],
           [InlineKeyboardButton(text="WB",
                                 callback_data='wb_cb')],
           [InlineKeyboardButton(text="⭕️Инструкция⭕️",
                                 url="https://t.me/mpkeshbek_ru")],
           [InlineKeyboardButton(text="🤝Поддержка🤝",
                                 url="https://t.me/mp_keshbekru")],]
    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord


def cancel():
    ikb = [[InlineKeyboardButton(text="Сбросить",
                                 callback_data='cancel')]]
    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord


def shopping():
    ikb = [[InlineKeyboardButton(text="🛍Товары🛍",
                                 url='https://mp-keshbek.ru/shop/')]]
    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord


def cancel_new_admin():
    ikb = [[InlineKeyboardButton(text="Отмена",
                                 callback_data="new_admin_cancel")]]
    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord


def cancel_del_admin():
    ikb = [[InlineKeyboardButton(text="Отмена",
                                 callback_data="del_admin_cancel")]]
    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord

def kb_check_order_one(user_id, order_id, quan_products_accept):
    ikb = [[InlineKeyboardButton(text="✅Подтвердить",
                                 callback_data=AcceptBuy(user_id=user_id,
                                                         order_id=order_id).pack()),
            InlineKeyboardButton(text="❌Отмена",
                                 callback_data=CancelBuy(user_id=user_id,
                                                         order_id=order_id).pack())],
           [InlineKeyboardButton(text=f"Подтвержденные ({quan_products_accept})",
                                 callback_data="accept_buy_products")],
           [InlineKeyboardButton(text="⭕️Инструкция⭕️",
                                 url="https://t.me/mpkeshbek_ru")],
           [InlineKeyboardButton(text="🤝Поддержка🤝",
                                 url="https://t.me/mp_keshbekru")],
           [InlineKeyboardButton(text="🛍Товары🛍",
                                 url="https://mp-keshbek.ru/shop/")]]

    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord


def kb_check_order_many(user_id, order_id, quan_products_accept, inline_page):
    ikb = [[InlineKeyboardButton(text="✅Подтвердить",
                                 callback_data=AcceptBuy(user_id=user_id,
                                                         order_id=order_id).pack()),
            InlineKeyboardButton(text="❌Отмена",
                                 callback_data=CancelBuy(user_id=user_id,
                                                         order_id=order_id).pack())],
           [InlineKeyboardButton(text="<<",
                                 callback_data="back_product"),
            InlineKeyboardButton(text=f"{inline_page}",
                                 callback_data="inline_page"),
            InlineKeyboardButton(text=">>",
                                 callback_data="next_product")],

           [InlineKeyboardButton(text=f"Подтвержденные ({quan_products_accept})",
                                 callback_data="accept_buy_products")],
           [InlineKeyboardButton(text="⭕️Инструкция⭕️",
                                 url="https://t.me/mpkeshbek_ru")],
           [InlineKeyboardButton(text="🤝Поддержка🤝",
                                 url="https://t.me/mp_keshbekru")],
           [InlineKeyboardButton(text="🛍Товары🛍",
                                 url="https://mp-keshbek.ru/shop/")]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keyboard


def base_inline_kb_post_auth(quan_products_not_accept, quan_products_accept):
    ikb = [[InlineKeyboardButton(text=f"Товары на подтверждение ({quan_products_not_accept})",
                                 callback_data="except_products")],
           [InlineKeyboardButton(text=f"Подтвержденные ({quan_products_accept})",
                                 callback_data="accept_buy_products")],
           [InlineKeyboardButton(text="⭕️Инструкция⭕️",
                                 url="https://t.me/mpkeshbek_ru")],
           [InlineKeyboardButton(text="🤝Поддержка🤝",
                                 url="https://t.me/mp_keshbekru")],
           [InlineKeyboardButton(text="🛍Товары🛍",
                                 url="https://mp-keshbek.ru/shop/")]]

    keybord = InlineKeyboardMarkup(inline_keyboard=ikb)
    return keybord









