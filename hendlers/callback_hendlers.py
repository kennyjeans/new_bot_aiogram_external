from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import URLInputFile, InputMediaPhoto, FSInputFile
import requests
from dop_func_bot.cb_data import AcceptBuy, CancelBuy
from external_wb_parser import check_user_orders
from keyboards.inline_kb import cancel, start_kb, kb_check_order_one, kb_check_order_many, base_inline_kb_post_auth
from state_bot import StateEmail, StatePhone, StateNewAdmin, StateDelAdmin
from aiogram.filters import StateFilter
from data_base.pg_db_func import delete_data_cancel_reg, delete_order, select_accept_orders
from data_base.aiosqlite_func import (insert_registration_data, delete_message_id_registration,
                                      select_registration, select_edit_products, check_new_products,
                                      insert_msd_products, new_insert_or_update_page_products,
                                      delete_items_for_confirmation, update_page_products, select_page_product)
from dop_func_bot.dop_func import delete_message
from utils import get_db_connection

cb_router = Router()


@cb_router.callback_query(F.data == "wb_cb", StateFilter(None))
async def wb_start_reg(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    message = await call.message.answer(text="<b>Введите почту:</b>\n\n<b>Пример:</b> pepa@example.ru",
                                        reply_markup=cancel(),
                                        parse_mode="HTML")
    await insert_registration_data(user_id=call.from_user.id,
                                   message_id=message.message_id)
    await state.set_state(StateEmail.email_state)


@cb_router.callback_query(F.data == "wb_cb", StateFilter("*"))
async def wb_start_reg(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    message = await call.message.answer(text="<b>Введите почту:</b>\n\n<b>Пример:</b> pepa@example.ru",
                                        reply_markup=cancel(),
                                        parse_mode="HTML")
    await insert_registration_data(user_id=call.from_user.id,
                                   message_id=message.message_id)
    await state.set_state(StateEmail.email_state)



@cb_router.callback_query(F.data == "cancel", StateFilter(StateEmail.email_state))
async def cancel_hendler_email(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.answer()
    messages = await select_registration(user_id=call.from_user.id)
    await delete_message(chat_id=call.from_user.id,
                         list_message_id=messages,
                         bot=bot)
    await delete_message_id_registration(user_id=call.from_user.id)
    messages_4 = await select_edit_products(user_id=call.from_user.id)
    await delete_message(chat_id=call.from_user.id,
                         list_message_id=messages,
                         bot=bot)
    await delete_message_id_registration(user_id=call.from_user.id)
    try:
        photo = FSInputFile(path="base_photo/cancel.png")
        media = InputMediaPhoto(media=photo,
                                caption=("Привет от mp-keshbek👋\n\n"
                                         "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                         "1. mp-keshbek.ru\n"
                                         "2. WildBerries (через данный бот)"),
                                parse_mode="HTML")
        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                               media=media,
                                               message_id=messages_4,
                                               reply_markup=start_kb())

        await insert_msd_products(user_id=call.from_user.id,
                                  message_id=message.message_id)
    except:
        photo = FSInputFile(path="base_photo/cancel.png")
        media = InputMediaPhoto(media=photo,
                                caption=("Привет от mp-keshbek👋\n\n"
                                         "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                         "1. mp-keshbek.ru\n"
                                         "2. WildBerries (через данный бот)"),
                                parse_mode="HTML")
        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                               media=media,
                                               message_id=messages_4,
                                               reply_markup=start_kb())

        await insert_msd_products(user_id=call.from_user.id,
                                  message_id=message.message_id)
    delete_data_cancel_reg(user_id=call.from_user.id)
    await state.clear()


@cb_router.callback_query(F.data == "cancel", StateFilter(StatePhone.phone_state))
async def cancel_hendler_phone(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.answer()
    messages = await select_registration(user_id=call.from_user.id)
    await delete_message(chat_id=call.from_user.id,
                         list_message_id=messages,
                         bot=bot)
    await delete_message_id_registration(user_id=call.from_user.id)
    messages_4 = await select_edit_products(user_id=call.from_user.id)
    await delete_message(chat_id=call.from_user.id,
                         list_message_id=messages,
                         bot=bot)
    await delete_message_id_registration(user_id=call.from_user.id)
    try:
        photo = FSInputFile(path="base_photo/cancel.png")
        media = InputMediaPhoto(media=photo,
                                caption=("Привет от mp-keshbek👋\n\n"
                                         "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                         "1. mp-keshbek.ru\n"
                                         "2. WildBerries (через данный бот)"),
                                parse_mode="HTML")
        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                               media=media,
                                               message_id=messages_4,
                                               reply_markup=start_kb())

        await insert_msd_products(user_id=call.from_user.id,
                                  message_id=message.message_id)
    except:
        photo = FSInputFile(path="base_photo/cancel.png")
        media = InputMediaPhoto(media=photo,
                                caption=("Привет от mp-keshbek👋\n\n"
                                         "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                         "1. mp-keshbek.ru\n"
                                         "2. WildBerries (через данный бот)"),
                                parse_mode="HTML")
        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                               media=media,
                                               message_id=messages_4,
                                               reply_markup=start_kb())

        await insert_msd_products(user_id=call.from_user.id,
                                  message_id=message.message_id)
    delete_data_cancel_reg(user_id=call.from_user.id)
    await state.clear()


@cb_router.callback_query(F.data == "new_admin_cancel", StateFilter(StateNewAdmin.new_admin_state))
async def cancel_new_admin_cb(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(text="Процесс назначения нового администратора сброшен")
    await state.clear()


@cb_router.callback_query(F.data == "del_admin_cancel", StateFilter(StateDelAdmin.del_admin_state))
async def cancel_new_admin_cb(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(text="Процесс удаления администратора сброшен")
    await state.clear()


@cb_router.callback_query(AcceptBuy.filter(), StateFilter(None))
async def check_order(call: types.CallbackQuery,
                      callback_data: AcceptBuy,
                      bot: Bot):
    """
    Проверяет заказ по его ID.
    """
    wp_order_id = callback_data.order_id
    conn = get_db_connection()
    cur = conn.cursor()
    st = '''
    select wp_products.product_id, order_id, chat_id, is_verified, phone_number from
    (select auth_user.phone_number as phone_number, auth_user.chat_id as chat_id, is_verified, order_id, wp_product_id from 
    (select id as order_id, customer_id, product_id as wp_product_id from wp_orders where id = %(wp_order_id)s) as t1
    left join auth_user 
    on t1.customer_id = auth_user.wp_id) as t2
    left join wp_products
    on t2.wp_product_id = wp_products.id
    '''
    try:
        cur.execute(st, {'wp_order_id': wp_order_id})
    except Exception as e:
        print(e)
    order_data = cur.fetchone()
    #print(order_data)
    if not order_data:
        await call.answer(text="ЗАКАЗ ПОКА НЕ НАЙДЕН ⌛️\n"
                               "Попробуйте позже")
        conn.close()
        #print(1)
        return
    if order_data[2] != str(call.from_user.id):
        await call.answer(text="ЗАКАЗ ПОКА НЕ НАЙДЕН ⌛️\n"
                               "Попробуйте позже")
        #print(3)
        return
    else:
        st_auth = '''
        select phone_number, chat_id, proxy_id, proxy_name, cookies, auth_token, user_agent 
        from auth_user 
        where is_verified is true and phone_number = %(phone_number)s and chat_id = %(chat_id)s
        '''

        cur.execute(st_auth, {'phone_number': order_data[4], 'chat_id': str(call.from_user.id)})
        auth_data = cur.fetchone()
        #print(auth_data)
        auth_data_dict = {auth_data[0]: {
            'cookies': auth_data[4],
            'auth_token': auth_data[5],
            'user_agent': auth_data[6],
            'proxy_name': auth_data[3],
            'chat_id': auth_data[1],
            'proxy_id': auth_data[2]
        }}

        #pprint(auth_data_dict, order_data[0], order_data[1])
        is_finded = check_user_orders(auth_data_dict, order_data[0], order_data[1])
        if is_finded:
            await delete_items_for_confirmation(call.from_user.id, order_id=int(wp_order_id))
            await call.answer('Заказ подтвержден ✅')
            conn.close()

            confirm_order_data = {"status": "completed",
                                 "order_id": int(wp_order_id),
                                 "token": "bk7ZubNZ1XuJXiXzDqyjgZPbopI8wK"}
            url = "https://mp-keshbek.ru/api/changeOrderStatus.php"
            data = requests.post(url, data=confirm_order_data)

            messages_4 = await select_edit_products(user_id=call.from_user.id)
            new_product = await check_new_products(user_id=call.from_user.id)
            #print(new_product)
            if new_product != []:
                last_new_product = new_product[0]
                photo = last_new_product[1]
                order_id = last_new_product[2]
                article = last_new_product[3]
                page = last_new_product[4]
                position = last_new_product[5]
                wb_search_url = last_new_product[6]
                quan_products_accept = select_accept_orders(chat_id=call.from_user.id)
                if quan_products_accept == []:
                    quan_products_accept = 0
                else:
                    quan_products_accept = len(quan_products_accept)

                if len(new_product) == 1:
                    try:
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                               user_id=call.from_user.id,
                                                                                               order_id=int(order_id)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                    except:
                        await call.answer()
                        photo = URLInputFile(photo)
                        message = await bot.send_photo(chat_id=call.from_user.id,
                                                       photo=photo,
                                                       caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                                f'<b>Артикул:</b> {article}\n'
                                                                f'<b>Карточка товара на странице:</b> {page}\n'
                                                                f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                                f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                                f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                                f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                                f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                       parse_mode="HTML",
                                                       reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                       user_id=call.from_user.id,
                                                                                       order_id=int(order_id)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)

                elif len(new_product) > 1:
                    try:
                        quantity_products = len(new_product)
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                                user_id=call.from_user.id,
                                                                                                order_id=int(order_id),
                                                                                                inline_page=f"1/{quantity_products}"))
                        await new_insert_or_update_page_products(user_id=call.from_user.id)
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                    except:
                        quantity_products = len(new_product)
                        photo = URLInputFile(photo)
                        message = await bot.send_photo(chat_id=call.from_user.id,
                                                       photo=photo,
                                                       reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                        user_id=call.from_user.id,
                                                                                        order_id=int(order_id),
                                                                                        inline_page=f"1/{quantity_products}"),
                                                       caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                                f'<b>Артикул:</b> {article}\n'
                                                                f'<b>Карточка товара на странице:</b> {page}\n'
                                                                f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                                f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                                f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                                f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                                f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                       parse_mode="HTML")
                        await new_insert_or_update_page_products(user_id=call.from_user.id)
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
            else:
                quan_products_accept = select_accept_orders(chat_id=call.from_user.id)
                if quan_products_accept == []:
                    quan_products_accept = 0
                else:
                    quan_products_accept = len(quan_products_accept)
                try:
                    try:

                        photo = FSInputFile(path="base_photo/basic_menu.png")
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'На данный момент у вас больше нет товаров на подтверждение☺️\n'
                                                         f'<i>Для обновления данных нажмите на интересующий вас раздел</i>☺️'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=base_inline_kb_post_auth(
                                                                               quan_products_accept=quan_products_accept,
                                                                               quan_products_not_accept=len(new_product)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                    except:
                        photo = FSInputFile(path="base_photo/basic_menu.png")
                        media = InputMediaPhoto(media=photo,
                                                caption=(
                                                    f'На данный момент у вас больше нет товаров на подтверждение☺️\n'
                                                    f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=base_inline_kb_post_auth(
                                                                   quan_products_accept=quan_products_accept,
                                                                   quan_products_not_accept=len(new_product)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)

                except:
                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    message = await bot.send_photo(chat_id=call.from_user.id,
                                                   caption=(
                                                       f'На данный момент у вас больше нет товаров на подтверждение☺️\n'
                                                       f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                                   parse_mode="HTML",
                                                   photo=photo,
                                                   reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
        else:
            await call.answer("ЗАКАЗ ПОКА НЕ НАЙДЕН ⌛️\n"
                               "Попробуйте позже")
            conn.close()
            return


@cb_router.callback_query(F.data == "back_product")
async def back_product(call: types.CallbackQuery, bot: Bot):
    data = await update_page_products(user_id=call.from_user.id, plus_minus="-")
    if data == False:
        await call.answer("Слева товаров больше нет")
    else:
        messages_4 = await select_edit_products(user_id=call.from_user.id)
        new_product = await check_new_products(user_id=call.from_user.id)
        page_product = await select_page_product(user_id=call.from_user.id)
        quan_products_accept = select_accept_orders(chat_id=call.from_user.id)
        if quan_products_accept == []:
            quan_products_accept = 0
        else:
            quan_products_accept = len(quan_products_accept)

        if new_product != []:
            last_new_product = new_product[page_product - 1]
            photo = last_new_product[1]
            order_id = last_new_product[2]
            article = last_new_product[3]
            page = last_new_product[4]
            position = last_new_product[5]
            wb_search_url = last_new_product[6]

            if len(new_product) == 1:
                try:
                    try:
                        await call.answer()
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                               user_id=call.from_user.id,
                                                                                               order_id=int(order_id)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                    except:
                        await call.answer()
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                               user_id=call.from_user.id,
                                                                                               order_id=int(order_id)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                except:
                    await call.answer()
                    photo = URLInputFile(photo)
                    message = await bot.send_photo(chat_id=call.from_user.id,
                                                   photo=photo,
                                                   caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                            f'<b>Артикул:</b> {article}\n'
                                                            f'<b>Карточка товара на странице:</b> {page}\n'
                                                            f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                            f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                            f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                            f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                            f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                   parse_mode="HTML",
                                                   reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                   user_id=call.from_user.id,
                                                                                   order_id=int(order_id)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)

            elif len(new_product) > 1:
                try:
                    try:
                        await call.answer()
                        quantity_products = len(new_product)
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                                user_id=call.from_user.id,
                                                                                                order_id=int(order_id),
                                                                                                inline_page=f"{page_product}/{quantity_products}"))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                    except:
                        await call.answer()
                        quantity_products = len(new_product)
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_many(
                                                                   quan_products_accept=quan_products_accept,
                                                                   user_id=call.from_user.id,
                                                                   order_id=int(order_id),
                                                                   inline_page=f"{page_product}/{quantity_products}"))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)

                except:
                    await call.answer()
                    quantity_products = len(new_product)
                    photo = URLInputFile(photo)
                    message = await bot.send_photo(chat_id=call.from_user.id,
                                                   photo=photo,
                                                   reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                    user_id=call.from_user.id,
                                                                                    order_id=int(order_id),
                                                                                    inline_page=f"{page_product}/{quantity_products}"),
                                                   caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                            f'<b>Артикул:</b> {article}\n'
                                                            f'<b>Карточка товара на странице:</b> {page}\n'
                                                            f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                            f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                            f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                            f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                            f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                   parse_mode="HTML")
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
        else:
            try:
                try:
                    await call.answer()
                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                     f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
                except:
                    await call.answer()
                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                     f'<i>Для обновления данных нажмите на интересующий вас раздел</i>😊'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
            except:
                await call.answer()
                photo = FSInputFile(path="base_photo/basic_menu.png")
                message = await bot.send_photo(chat_id=call.from_user.id,
                                               caption=(
                                                   f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                   f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                               parse_mode="HTML",
                                               photo=photo,
                                               reply_markup=base_inline_kb_post_auth(
                                                   quan_products_accept=quan_products_accept,
                                                   quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)


@cb_router.callback_query(F.data == "next_product")
async def back_product(call: types.CallbackQuery, bot: Bot):
    data = await update_page_products(user_id=call.from_user.id, plus_minus="+")
    quan_products_accept = select_accept_orders(chat_id=call.from_user.id)
    if quan_products_accept == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept)
    if data == False:
        await call.answer("Справа товаров больше нет")
    else:
        messages_4 = await select_edit_products(user_id=call.from_user.id)
        new_product = await check_new_products(user_id=call.from_user.id)
        page_product = await select_page_product(user_id=call.from_user.id)
        #print(new_product)
        if new_product != []:
            last_new_product = new_product[page_product - 1]
            photo = last_new_product[1]
            order_id = last_new_product[2]
            article = last_new_product[3]
            page = last_new_product[4]
            position = last_new_product[5]
            wb_search_url = last_new_product[6]

            if len(new_product) == 1:
                try:
                    try:
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                               user_id=call.from_user.id,
                                                                                               order_id=int(order_id)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                        await call.answer()
                    except:
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>☺️'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                               user_id=call.from_user.id,
                                                                                               order_id=int(order_id)))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                        await call.answer()
                except:
                    photo = URLInputFile(photo)
                    message = await bot.send_photo(chat_id=call.from_user.id,
                                                   photo=photo,
                                                   caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                            f'<b>Артикул:</b> {article}\n'
                                                            f'<b>Карточка товара на странице:</b> {page}\n'
                                                            f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                            f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                            f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                            f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                            f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                   parse_mode="HTML",
                                                   reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                   user_id=call.from_user.id,
                                                                                   order_id=int(order_id)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
                    await call.answer()

            elif len(new_product) > 1:
                try:
                    try:
                        quantity_products = len(new_product)
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                                user_id=call.from_user.id,
                                                                                                order_id=int(order_id),
                                                                                                inline_page=f"{page_product}/{quantity_products}"))
                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                        await call.answer()
                    except:
                        quantity_products = len(new_product)
                        photo = URLInputFile(photo)
                        media = InputMediaPhoto(media=photo,
                                                caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                         f'<b>Артикул:</b> {article}\n'
                                                         f'<b>Карточка товара на странице:</b> {page}\n'
                                                         f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                         f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                         f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                         f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                         f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                parse_mode="HTML")
                        message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                               media=media,
                                                               message_id=messages_4,
                                                               reply_markup=kb_check_order_many(
                                                                   quan_products_accept=quan_products_accept,
                                                                   user_id=call.from_user.id,
                                                                   order_id=int(order_id),
                                                                   inline_page=f"{page_product}/{quantity_products}"))

                        await insert_msd_products(user_id=call.from_user.id,
                                                  message_id=message.message_id)
                        await call.answer()
                except:
                    quantity_products = len(new_product)
                    photo = URLInputFile(photo)
                    message = await bot.send_photo(chat_id=call.from_user.id,
                                                   photo=photo,
                                                   reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                    user_id=call.from_user.id,
                                                                                    order_id=int(order_id),
                                                                                    inline_page=f"{page_product}/{quantity_products}"),
                                                   caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                            f'<b>Артикул:</b> {article}\n'
                                                            f'<b>Карточка товара на странице:</b> {page}\n'
                                                            f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                            f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                            f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                            f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                            f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                                   parse_mode="HTML")

                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
                    await call.answer()
        else:
            try:
                try:
                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                     f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
                    await call.answer()
                except:
                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                     f'<i>Для обновления данных нажмите на интересующий вас раздел</i>☺️'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=call.from_user.id,
                                              message_id=message.message_id)
                    await call.answer()
            except:

                photo = FSInputFile(path="base_photo/basic_menu.png")
                message = await bot.send_photo(chat_id=call.from_user.id,
                                               caption=(
                                                   f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                   f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                               parse_mode="HTML",
                                               photo=photo,
                                               reply_markup=base_inline_kb_post_auth(
                                                   quan_products_accept=quan_products_accept,
                                                   quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
                await call.answer()


@cb_router.callback_query(F.data == "except_products")
async def except_products(call: types.CallbackQuery, bot: Bot):
    messages_4 = await select_edit_products(user_id=call.from_user.id)
    new_product = await check_new_products(user_id=call.from_user.id)
    quan_products_accept = select_accept_orders(chat_id=call.from_user.id)
    if quan_products_accept == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept)

    if len(new_product) == 1:
        last_new_product = new_product[0]
        photo = last_new_product[1]
        order_id = last_new_product[2]
        article = last_new_product[3]
        page = last_new_product[4]
        position = last_new_product[5]
        wb_search_url = last_new_product[6]
        try:
            await call.answer()
            photo = URLInputFile(photo)
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                             f'<b>Артикул:</b> {article}\n'
                                             f'<b>Карточка товара на странице:</b> {page}\n'
                                             f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                             f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                             f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                             f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                             f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                   user_id=call.from_user.id,
                                                                                   order_id=int(order_id)))
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
        except:
            await call.answer()
            photo = URLInputFile(photo)
            message = await bot.send_photo(chat_id=call.from_user.id,
                                           photo=photo,
                                           caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                    f'<b>Артикул:</b> {article}\n'
                                                    f'<b>Карточка товара на странице:</b> {page}\n'
                                                    f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                    f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                    f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                    f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                    f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>☺️'),
                                           parse_mode="HTML",
                                           reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                           user_id=call.from_user.id,
                                                                           order_id=int(order_id)))
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
    elif len(new_product) == 0:
        await call.answer("Заказов нет")
        try:
            try:
                await call.answer()
                photo = FSInputFile(path="base_photo/basic_menu.png")
                media = InputMediaPhoto(media=photo,
                                        caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                 f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=base_inline_kb_post_auth(
                                                           quan_products_accept=quan_products_accept,
                                                           quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
            except:
                await call.answer()
                photo = FSInputFile(path="base_photo/basic_menu.png")
                media = InputMediaPhoto(media=photo,
                                        caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                 f'<i>Для обновления данных нажмите на интересующий вас раздел</i>☺️'),
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=base_inline_kb_post_auth(
                                                           quan_products_accept=quan_products_accept,
                                                           quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
        except:
            await call.answer()
            photo = FSInputFile(path="base_photo/basic_menu.png")
            message = await bot.send_photo(chat_id=call.from_user.id,
                                           caption=(
                                               f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                               f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                           parse_mode="HTML",
                                           photo=photo,
                                           reply_markup=base_inline_kb_post_auth(
                                               quan_products_accept=quan_products_accept,
                                               quan_products_not_accept=len(new_product)))
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
    else:
        last_new_product = new_product[0]
        photo = last_new_product[1]
        order_id = last_new_product[2]
        article = last_new_product[3]
        page = last_new_product[4]
        position = last_new_product[5]
        wb_search_url = last_new_product[6]
        try:
            await call.answer()
            quantity_products = len(new_product)
            photo = URLInputFile(photo)
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                             f'<b>Артикул:</b> {article}\n'
                                             f'<b>Карточка товара на странице:</b> {page}\n'
                                             f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                             f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                             f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                             f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                             f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                    user_id=call.from_user.id,
                                                                                    order_id=int(order_id),
                                                                                    inline_page=f"1/{quantity_products}"))
            await new_insert_or_update_page_products(user_id=call.from_user.id)
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
        except:
            await call.answer()
            quantity_products = len(new_product)
            photo = URLInputFile(photo)
            message = await bot.send_photo(chat_id=call.from_user.id,
                                           photo=photo,
                                           reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                            user_id=call.from_user.id,
                                                                            order_id=int(order_id),
                                                                            inline_page=f"1/{quantity_products}"),
                                           caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                    f'<b>Артикул:</b> {article}\n'
                                                    f'<b>Карточка товара на странице:</b> {page}\n'
                                                    f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                    f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                    f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                    f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                    f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                           parse_mode="HTML")
            await new_insert_or_update_page_products(user_id=call.from_user.id)
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)


@cb_router.callback_query(CancelBuy.filter(), StateFilter(None))
async def check_order(call: types.CallbackQuery,
                      callback_data: CancelBuy,
                      bot: Bot):
    wp_order_id = callback_data.order_id
    print(wp_order_id, type(wp_order_id))
    delete_order_data = {"status": "cancelled",
                         "order_id": int(wp_order_id),
                         "token": "bk7ZubNZ1XuJXiXzDqyjgZPbopI8wK"}
    url = "https://mp-keshbek.ru/api/changeOrderStatus.php"
    data = requests.post(url, data=delete_order_data)
    delete_order(wp_order_id)
    print(data)
    quan_products_accept = select_accept_orders(chat_id=call.from_user.id)
    if quan_products_accept == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept)

    await delete_items_for_confirmation(call.from_user.id, order_id=int(wp_order_id))
    messages_4 = await select_edit_products(user_id=call.from_user.id)
    new_product = await check_new_products(user_id=call.from_user.id)

    if len(new_product) == 1:
        last_new_product = new_product[0]

        photo = last_new_product[1]
        order_id = last_new_product[2]
        article = last_new_product[3]
        page = last_new_product[4]
        position = last_new_product[5]
        wb_search_url = last_new_product[6]
        try:
            await call.answer()
            photo = URLInputFile(photo)
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                             f'<b>Артикул:</b> {article}\n'
                                             f'<b>Карточка товара на странице:</b> {page}\n'
                                             f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                             f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                             f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                             f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                             f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                   user_id=call.from_user.id,
                                                                                   order_id=int(order_id)))
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
        except:
            await call.answer()
            photo = URLInputFile(photo)
            message = await bot.send_photo(chat_id=call.from_user.id,
                                           photo=photo,
                                           caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                    f'<b>Артикул:</b> {article}\n'
                                                    f'<b>Карточка товара на странице:</b> {page}\n'
                                                    f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                    f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                    f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                    f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                    f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                           parse_mode="HTML",
                                           reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                           user_id=call.from_user.id,
                                                                           order_id=int(order_id)))
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
    elif len(new_product) == 0:
        await call.answer("Заказ отменен\nЗаказов больше нет")
        try:
            try:
                await call.answer()
                photo = FSInputFile(path="base_photo/basic_menu.png")
                media = InputMediaPhoto(media=photo,
                                        caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                 f'<i>Для обновления данных нажмите на интересующий вас раздел</i>☺️'),
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=base_inline_kb_post_auth(
                                                           quan_products_accept=quan_products_accept,
                                                           quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
            except:
                await call.answer()
                photo = FSInputFile(path="base_photo/basic_menu.png")
                media = InputMediaPhoto(media=photo,
                                        caption=(f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                                 f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=base_inline_kb_post_auth(
                                                           quan_products_accept=quan_products_accept,
                                                           quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
        except:
            await call.answer()
            photo = FSInputFile(path="base_photo/basic_menu.png")
            message = await bot.send_photo(chat_id=call.from_user.id,
                                           caption=(
                                               f'На данный момент у вас нет товаров на подтверждение☺️\n'
                                               f'<i>Для обновления данных нажмите на интересующий вас раздел</i>'),
                                           parse_mode="HTML",
                                           photo=photo,
                                           reply_markup=base_inline_kb_post_auth(
                                               quan_products_accept=quan_products_accept,
                                               quan_products_not_accept=len(new_product)))
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)

    else:
        last_new_product = new_product[0]
        photo = last_new_product[1]
        order_id = last_new_product[2]
        article = last_new_product[3]
        page = last_new_product[4]
        position = last_new_product[5]
        wb_search_url = last_new_product[6]
        try:
            await call.answer("Заказ отменен")
            quantity_products = len(new_product)
            photo = URLInputFile(photo)
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                             f'<b>Артикул:</b> {article}\n'
                                             f'<b>Карточка товара на странице:</b> {page}\n'
                                             f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                             f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                             f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                             f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                             f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                    user_id=call.from_user.id,
                                                                                    order_id=int(order_id),
                                                                                    inline_page=f"1/{quantity_products}"))
            await new_insert_or_update_page_products(user_id=call.from_user.id)
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)
        except:
            await call.answer("Заказ отменен")
            quantity_products = len(new_product)
            photo = URLInputFile(photo)
            message = await bot.send_photo(chat_id=call.from_user.id,
                                           photo=photo,
                                           reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                            user_id=call.from_user.id,
                                                                            order_id=int(order_id),
                                                                            inline_page=f"1/{quantity_products}"),
                                           caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                    f'<b>Артикул:</b> {article}\n'
                                                    f'<b>Карточка товара на странице:</b> {page}\n'
                                                    f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                    f'<b>Ссылка для поиска товара:</b> <a href="{wb_search_url}">ссылка</a>\n\n'
                                                    f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                    f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                    f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                           parse_mode="HTML")
            await new_insert_or_update_page_products(user_id=call.from_user.id)
            await insert_msd_products(user_id=call.from_user.id,
                                      message_id=message.message_id)


@cb_router.callback_query(F.data == "accept_buy_products")
async def back_product(call: types.CallbackQuery, bot: Bot):
    messages_4 = await select_edit_products(user_id=call.from_user.id)
    new_product = await check_new_products(user_id=call.from_user.id)
    quan_products_accept_data = select_accept_orders(chat_id=call.from_user.id)
    if quan_products_accept_data == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept_data)

    if quan_products_accept == 0:
        await call.answer("Подтвержденных заказов нет")
        return
    else:
        full_text_message = ''
        for order in quan_products_accept_data:
            text_message = (f"Артикул: {order[0]}\n"
                            f"Номер заказа: {order[1]}\n\n")
            full_text_message += text_message
            try:
                await call.answer()
                photo = FSInputFile(path="base_photo/accept_products.png")
                media = InputMediaPhoto(media=photo,
                                        caption="☺️" + full_text_message,
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=base_inline_kb_post_auth(
                                                           quan_products_accept=quan_products_accept,
                                                           quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
            except:
                await call.answer()
                photo = FSInputFile(path="base_photo/accept_products.png")
                media = InputMediaPhoto(media=photo,
                                        caption=full_text_message,
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=call.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=base_inline_kb_post_auth(
                                                           quan_products_accept=quan_products_accept,
                                                           quan_products_not_accept=len(new_product)))
                await insert_msd_products(user_id=call.from_user.id,
                                          message_id=message.message_id)
                await call.answer()



