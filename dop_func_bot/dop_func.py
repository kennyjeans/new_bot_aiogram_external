import asyncio

import psycopg2
from fake_useragent import UserAgent
from aiogram import Bot, Router
from data_base.aiosqlite_func import (select_registration, delete_message_id_registration, insert_registration_data,
                                      delete_edit_start_auth, select_edit_start_auth, select_admins, set_state_auth,
                                      state_clear_auth, select_cp_sms, delete_edit_wb_auth, select_edit_wb_auth,
                                      update_resend, delete_sms_cp, select_edit_products, clear_edit_products,
                                      insert_msd_products, check_new_products,
                                      new_insert_or_update_page_products)
from data_base.pg_db_func import clear_db_auth_user, select_accept_orders
from keyboards.inline_kb import start_kb, shopping, base_inline_kb_post_auth, kb_check_order_one, kb_check_order_many
from settings import TG_TOKEN
from utils import get_db_connection
from aiogram.types import FSInputFile, InputMediaPhoto, InputFile, URLInputFile

ua = UserAgent(platforms='pc', os=["windows", "macos"], browsers='chrome')
router_storage = Router()


async def delete_message(chat_id, list_message_id, bot: Bot):
    for message_id in list_message_id:
        print(list_message_id)
        message_id = message_id[0]
        try:
            await bot.delete_message(chat_id=chat_id,
                                     message_id=message_id,
                                     request_timeout=None)
        except:
            continue


def try_write_new_tg_user(chat_id, phone_number, selenium_id, email):
    """
    Пытается записать нового пользователя Telegram в базу данных.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"select proxy_name, proxy_id from auth_user where phone_number = %(phone_number)s",
                {'phone_number': phone_number})
    proxy_data = cur.fetchone()
    print(proxy_data)

    if not proxy_data[0] and not proxy_data[1]:
        cur.execute('select proxy_name, proxy_id from proxy where is_busy is false and is_healthy is true limit 1')
        proxy_data = cur.fetchone()
        print(proxy_data)

    if proxy_data:
        proxy_name, proxy_id = proxy_data
        cur.execute(f'update proxy set is_busy = true where proxy_id = %(proxy_id)s',
                    {'proxy_id': proxy_id})
        cur.execute(f'update selenium_process set is_busy = true where process_id = %(selenium_id)s',
                    {'selenium_id': selenium_id})
        conn.commit()
        data = (str(email), str(chat_id), str(phone_number), int(selenium_id), False, str(proxy_name), str(proxy_id), str(ua.random))
        print(data)

        try:
            print('Процесс начат')
            insert_statement = """
                INSERT INTO auth_user (wp_email, chat_id, phone_number, selenium_id, is_verified, proxy_name, proxy_id, user_agent) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (wp_email) 
                DO UPDATE SET selenium_id = excluded.selenium_id,
                               chat_id = excluded.chat_id,
                               phone_number = excluded.phone_number,
                               is_verified = false,
                               proxy_name = excluded.proxy_name,
                               proxy_id = excluded.proxy_id,
                               user_agent = excluded.user_agent
                """
            cur.execute(insert_statement, data)
            conn.commit()
            conn.close()
        except psycopg2.Error as e:
            print(f"Ошибка: {e}")

        print('Процесс закончен ')
        return True
    else:
        conn.close()
        return False


def check_free_selenium(chat_id, phone_number, email=None):
    """
    Проверяет наличие свободных Selenium процессов и статус пользователя.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('select process_id from selenium_process where is_busy is false order by process_id asc limit 1')
    process_id = cur.fetchone()
    print(process_id)
    if process_id:
        process_id = process_id[0]
    cur.execute(f'select * from auth_user where chat_id = %(chat_id)s and selenium_id > 0',
                {'chat_id': f'{chat_id}'})
    print(cur.fetchone())
    cur.execute(f'select count(*) from auth_user where chat_id = %(chat_id)s and selenium_id > 0',
                {'chat_id': f'{chat_id}'})
    count_open_registration = cur.fetchone()[0]
    print('1,', count_open_registration)
    if email:
        cur.execute(f"select is_verified from auth_user where wp_email = %(email)s",
                    {'email': email})
        print('1,', process_id)
    else:
        cur.execute(f"select is_verified from auth_user where phone_number = %(phone_number)s",
                    {'phone_number': phone_number})
    is_verified = cur.fetchone()
    conn.close()
    if is_verified:
        if is_verified[0] is True:
            return '1' #'Вы уже авторизованы'
    if process_id and count_open_registration == 0:
        return process_id
    elif process_id and count_open_registration > 0:
        print(process_id, count_open_registration)
        return '2' #'У вас уже начат процесс авторизации.\n Нужно немного пождождать до ее окончания'
    else:
        return '3' #'Все браузеры в данный момент заняты, попробуйте авторизоваться позже'


#уведомление о неудачной авторизации
#1.Рассылка администрации о проблеме
#2.Взаимосдействие с aiosql
#3.Удаление всех данных из pg бд (кроме внешних)
async def bad_registration(user_id, errors):
    bot = Bot(token=TG_TOKEN, session=None)

    user_id = int(user_id)
    messages = await select_registration(user_id=user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)
    if messages_3 != [] and messages_2 != []:
        messages = messages + messages_2 + messages_3
    elif messages_3 == [] and messages_2 != []:
        messages = messages + messages_2
    elif messages_3 != [] and messages_2 == []:
        messages = messages + messages_3
    else:
        messages = messages
    #print(messages)
    await delete_message(chat_id=user_id,
                         list_message_id=messages,
                         bot=bot)

    await delete_message_id_registration(user_id=user_id)
    await delete_edit_start_auth(user_id=user_id)
    await delete_edit_wb_auth(user_id=user_id)
    messages_4 = await select_edit_products(user_id=user_id)
    photo = FSInputFile("base_photo/error_auth.png")
    if messages_4 == None:
        message = await bot.send_photo(chat_id=user_id,
                                       caption=('<b>☹️ПРИ АВТОРИЗАЦИИ ПРОИЗОШЛА ОШИБКА☹️</b>\n'
                                               'Бот уже уведомил поддержку\n\n'
                                               '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                               'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                               '1. mp-keshbek.ru\n'
                                               '2. WB (через данный бот)'),
                                       photo=photo,
                                       reply_markup=start_kb(),
                                       parse_mode="HTML")
        await state_clear_auth(user_id=user_id)
        await insert_msd_products(user_id=user_id,
                                  message_id=message.message_id)
    else:
        try:
            media = InputMediaPhoto(media=photo,
                                    caption=('<b>☹️ПРИ АВТОРИЗАЦИИ ПРОИЗОШЛА ОШИБКА☹️</b>\n'
                                               'Бот уже уведомил поддержку\n\n'
                                               '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                               'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                               '1. mp-keshbek.ru\n'
                                               '2. WB (через данный бот)'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
            await state_clear_auth(user_id=user_id)
        except Exception as e:
            print(e ,'я сломался')
            media = InputMediaPhoto(media=photo,
                                    caption=('<b>☹️ПРИ АВТОРИЗАЦИИ ПРОИЗОШЛА ОШИБКА☹️</b>\n'
                                             'Бот уже уведомил поддержку.\n\n'
                                             '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                             'Для начала работы требуется авторизация на 2-ух сайтах:☺️\n'
                                             '1. mp-keshbek.ru\n'
                                             '2. WB (через данный бот)'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)

            await state_clear_auth(user_id=user_id)

    admins = await select_admins()
    for admin in admins:
        try:
            await bot.send_message(chat_id=admin[0],
                                   text=("У данного пользователя возникли проблемы"
                                         " с авторизацией.\n\n"
                                         f"Ошибка имеет следующую формулировку: {errors}\n"
                                         "Данные пользовтеля:\n"
                                         f"user_id: {user_id}"))
        except Exception as e:
            print(f"Данному администратору не было выслано уведомление об ошибке, т.к {e}")
    await bot.session.close()


async def long_auth(user_id):
    bot = Bot(token=TG_TOKEN, session=None)

    user_id = int(user_id)
    messages = await select_registration(user_id=user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)
    if messages_3 != []:
        messages = messages + messages_2 + messages_3
    else:
        messages = messages + messages_2

    await delete_message(chat_id=user_id,
                         list_message_id=messages,
                         bot=bot)

    await delete_message_id_registration(user_id=user_id)
    await delete_edit_start_auth(user_id=user_id)
    await delete_edit_wb_auth(user_id=user_id)
    messages_4 = await select_edit_products(user_id=user_id)
    photo = FSInputFile("base_photo/long_auth.png")
    if messages_4 != None:
        message = await bot.send_photo(chat_id=user_id,
                                       photo=photo,
                                       caption=('<b>☹️ПРЕВЫШЕНО ВРЕМЯ АВТОРИЗАЦИИ☹️</b>\n\n'
                                               'Для начала требуется авторизация на 2-ух сайтах:\n'
                                               '1. mp-keshbek.ru\n'
                                               '2. WB (через данный бот)'),
                                       reply_markup=start_kb(),
                                       parse_mode="HTML")
        await insert_msd_products(user_id=user_id,
                                  message_id=message.message_id)
    else:
        try:
            media = InputMediaPhoto(media=photo,
                                    caption=('<b>☹️ПРЕВЫШЕНО ВРЕМЯ АВТОРИЗАЦИИ☹️</b>\n\n'
                                             'Для начала требуется авторизация на 2-ух сайтах:\n'
                                             '1. mp-keshbek.ru\n'
                                             '2. WB (через данный бот)'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
        except:
            media = InputMediaPhoto(media=photo,
                                    caption=('<b>☹️ПРЕВЫШЕНО ВРЕМЯ АВТОРИЗАЦИИ☹️</b>\n\n'
                                             'Для начала требуется авторизация на 2-ух сайтах☺️:\n'
                                             '1. mp-keshbek.ru\n'
                                             '2. WB (через данный бот)'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)

    await state_clear_auth(user_id=user_id)
    await bot.session.close()


async def sms_registration(user_id):
    bot = Bot(token=TG_TOKEN, session=None)
    user_id = int(user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)
    if messages_2 == []:
        if messages_3 == []:
            message = await bot.send_message(chat_id=user_id,
                                             text=('<b>🙂ВАМ ВЫСЛАН КОД ПОДТВЕРЖДЕНИЯ🙂</b>\n\n'
                                                   '<b>Пришлите код подтверждения</b>\n'
                                                   'Пример: 777555'),
                                             parse_mode="HTML")
        else:
            message = await bot.edit_message_text(chat_id=user_id,
                                                  text=('<b>🙂ВАМ ВЫСЛАН КОД ПОДТВЕРЖДЕНИЯ🙂</b>\n\n'
                                                        '<b>Пришлите код подтверждения</b>\n'
                                                        'Пример: 777555'),
                                                  message_id=messages_3[0][0],
                                                  parse_mode="HTML")
            await delete_edit_wb_auth(user_id=user_id)
    else:
        message = await bot.edit_message_text(chat_id=user_id,
                                              text=('<b>🙂ВАМ ВЫСЛАН КОД ПОДТВЕРЖДЕНИЯ🙂</b>\n\n'
                                                    '<b>Пришлите код подтверждения</b>\n'
                                                    'Пример: 777555'),
                                              message_id=messages_2[0][0],
                                              parse_mode="HTML")
        await delete_edit_start_auth(user_id=user_id)
    await set_state_auth(user_id=user_id,
                         state="sms")
    await insert_registration_data(user_id=user_id,
                                   message_id=message.message_id)
    await bot.session.close()


async def new_sms_registration(user_id):
    bot = Bot(token=TG_TOKEN, session=None)
    user_id = int(user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)

    if messages_2 == []:
        if messages_3 == []:
            message = await bot.send_message(chat_id=user_id,
                                             text=('<b>🔸КОД НЕ ПОДОШЕЛ🔸</b>\n\n'
                                                   '<b>😌ВВЕДИТЕ КОД ПОВТОРНО😌</b>\n\n'
                                                   '<b>Пришлите код подтверждения</b>\n'
                                                   'Пример: 777555'),
                                             parse_mode="HTML")
        else:
            message = await bot.edit_message_text(chat_id=user_id,
                                                  text=('<b>🔸КОД НЕ ПОДОШЕЛ🔸</b>\n\n'
                                                        '<b>😌ВВЕДИТЕ КОД ПОВТОРНО😌</b>\n\n'
                                                        '<b>Пришлите код подтверждения</b>\n'
                                                        'Пример: 777555'),
                                                  message_id=messages_3[0][0],
                                                  parse_mode="HTML")
            await delete_edit_wb_auth(user_id=user_id)
    else:
        await delete_edit_start_auth(user_id=user_id)
        message = await bot.edit_message_text(chat_id=user_id,
                                              text=('<b>🔸КОД НЕ ПОДОШЕЛ🔸</b>\n\n'
                                                    '<b>😌ВВЕДИТЕ КОД ПОВТОРНО😌</b>'
                                                    '<b>Пришлите код подтверждения</b>\n'
                                                    'Пример: 777555'),
                                              message_id=messages_2[0][0],
                                              parse_mode="HTML")

    await set_state_auth(user_id=user_id,
                         state="sms")
    await insert_registration_data(user_id=user_id,
                                   message_id=message.message_id)
    await bot.session.close()


async def resend_sms_registration(user_id):
    bot = Bot(token=TG_TOKEN, session=None)
    user_id = int(user_id)
    #message = await bot.send_message(chat_id=user_id,
    #                                 text='<b>☹️КОД НЕ СООТВЕТСТВУЕТ☹️</b>',
    #                                 parse_mode="HTML")
    await set_state_auth(user_id=user_id,
                         state="sms")
    #await insert_registration_data(user_id=user_id,
    #                               message_id=message.message_id)
    await bot.session.close()


async def long_captcha_input(user_id):
    bot = Bot(token=TG_TOKEN, session=None)

    user_id = int(user_id)
    messages = await select_registration(user_id=user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)
    messages_4 = await select_edit_products(user_id=user_id)
    messages = messages + messages_2
    if messages_3 == []:
        messages = messages + messages_2
    else:
        messages = messages + messages_2 + messages_3
    await delete_message(chat_id=user_id,
                         list_message_id=messages,
                         bot=bot)
    await delete_edit_wb_auth(user_id=user_id)
    await delete_message_id_registration(user_id=user_id)
    await delete_edit_start_auth(user_id=user_id)
    photo = FSInputFile("base_photo/long_captcha.png")
    if messages_4 == None:
        message = await bot.send_photo(chat_id=user_id,
                                       caption=('<b>☹️ПРЕВЫШЕНО ВРЕМЯ ОЖИДАНИЯ КАПЧИ, АВОРИЗУЙТЕСЬ ЗАНОВО☹️</b>\n\n'
                                                '<b>Для начала работы требуется авторизация на 2-ух сайтах:</b>\n'
                                                '1. mp-keshbek.ru\n'
                                                '2. WB (через данный бот)'),
                                       reply_markup=start_kb(),
                                       photo=photo,
                                       parse_mode="HTML")
        await insert_msd_products(user_id=user_id,
                                  message_id=message.message_id)
    else:
        try:
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>☹️ПРЕВЫШЕНО ВРЕМЯ ОЖИДАНИЯ КАПЧИ, АВОРИЗУЙТЕСЬ ЗАНОВО☹️</b>\n\n'
                                                    '<b>Для начала работы требуется авторизация на 2-ух сайтах:</b>\n'
                                                    '1. mp-keshbek.ru\n'
                                                    '2. WB (через данный бот)'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
        except:
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>☹️ПРЕВЫШЕНО ВРЕМЯ ОЖИДАНИЯ КАПЧИ, АВОРИЗУЙТЕСЬ ЗАНОВО☹️</b>\n\n'
                                             '<b>Для начала работы требуется авторизация на 2-ух сайтах😊:</b>\n'
                                             '1. mp-keshbek.ru\n'
                                             '2. WB (через данный бот)'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
    await state_clear_auth(user_id=user_id)
    await bot.session.close()


async def captcha_registration(user_id):
    bot = Bot(token=TG_TOKEN, session=None)
    user_id = int(user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)
    photo = FSInputFile(path=f"captchas/{user_id}.png")
    cp_data = await select_cp_sms(user_id=user_id, find_is="cp")
    resend_data = await select_cp_sms(user_id=user_id, find_is="resend")

    if cp_data != resend_data:
        if messages_2 != [] and messages_3 != []:
            await delete_message(chat_id=user_id,
                                 list_message_id=messages_2 + messages_3,
                                 bot=bot)
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🙂<b>ВВЕДИТЕ КАПЧУ</b>🙂\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await delete_edit_start_auth(user_id=user_id)
            await delete_edit_wb_auth(user_id=user_id)
            await set_state_auth(user_id=int(user_id), state="cp")

        elif messages_2 != [] and messages_3 == []:
            await delete_message(chat_id=user_id,
                                 list_message_id=messages_2,
                                 bot=bot)
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🙂<b>ВВЕДИТЕ КАПЧУ</b>🙂\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await delete_edit_start_auth(user_id=user_id)
            await set_state_auth(user_id=int(user_id), state="cp")

        elif messages_2 == [] and messages_3 != []:
            await delete_message(chat_id=user_id,
                                 list_message_id=messages_3,
                                 bot=bot)
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🙂<b>ВВЕДИТЕ КАПЧУ</b>🙂\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await delete_edit_wb_auth(user_id=user_id)
            await set_state_auth(user_id=int(user_id), state="cp")
        else:
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🙂<b>ВВЕДИТЕ КАПЧУ</b>🙂\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await set_state_auth(user_id=int(user_id), state="cp")

    else:
        if messages_2 != [] and messages_3 != []:
            await delete_message(chat_id=user_id,
                                 list_message_id=messages_3 + messages_2,
                                 bot=bot)
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🔸<b>КОД ПОДТВЕРЖДЕНИЯ НЕВЕРНЫЙ</b>🔸\n\n🙂<b>ВВЕДИТЕ КАПЧУ🙂</b>\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await delete_edit_start_auth(user_id=user_id)
            await delete_edit_wb_auth(user_id=user_id)
            await set_state_auth(user_id=int(user_id), state="cp")
            #await update_resend(user_id=user_id)

        elif messages_2 != [] and messages_3 == []:
            await delete_message(chat_id=user_id,
                                 list_message_id=messages_2,
                                 bot=bot)
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🔸<b>КОД ПОДТВЕРЖДЕНИЯ НЕВЕРНЫЙ</b>🔸\n\n🙂<b>ВВЕДИТЕ КАПЧУ🙂</b>\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await delete_edit_start_auth(user_id=user_id)
            await set_state_auth(user_id=int(user_id), state="cp")
            #await update_resend(user_id=user_id)

        elif messages_2 == [] and messages_3 != []:
            await delete_message(chat_id=user_id,
                                 list_message_id=messages_3,
                                 bot=bot)
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🔸<b>КОД ПОДТВЕРЖДЕНИЯ НЕВЕРНЫЙ</b>🔸\n\n🙂<b>ВВЕДИТЕ КАПЧУ🙂</b>\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await delete_edit_wb_auth(user_id=user_id)
            await set_state_auth(user_id=int(user_id), state="cp")
            #await update_resend(user_id=user_id)
        else:
            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption="🔸<b>КОД ПОДТВЕРЖДЕНИЯ НЕВЕРНЫЙ</b>🔸\n\n🙂<b>ВВЕДИТЕ КАПЧУ🙂</b>\n"
                                                   "Пример: PS1VG4",
                                           parse_mode="HTML")
            await set_state_auth(user_id=int(user_id), state="cp")
            #await update_resend(user_id=user_id)

    await insert_registration_data(user_id=user_id,
                                   message_id=message.message_id)
    await bot.session.close()


async def good_auth(user_id):
    bot = Bot(token=TG_TOKEN, session=None)

    user_id = int(user_id)
    messages = await select_registration(user_id=user_id)
    messages_2 = await select_edit_start_auth(user_id=user_id)
    messages_3 = await select_edit_wb_auth(user_id=user_id)
    messages_4 = await select_edit_products(user_id=user_id)
    print(messages_4)
    new_product = await check_new_products(user_id=user_id)
    quan_products_accept = select_accept_orders(chat_id=user_id)
    if quan_products_accept == []:
        quan_products_accept = 0

    else:
        quan_products_accept = len(quan_products_accept)


    if messages_4 != None:
        await delete_message(chat_id=user_id,
                             list_message_id=messages + messages_2 + messages_3,
                             bot=bot)
        await delete_message_id_registration(user_id=user_id)
        await delete_edit_start_auth(user_id=user_id)
        await delete_edit_wb_auth(user_id=user_id)
        photo = FSInputFile(path="base_photo/good_auth.png")
        try:
            media = InputMediaPhoto(media=photo,
                                    caption='<i>Если по каким-то причинам авторизация на wb будет'
                                              ' сброшена, бот вас об этом уведомит</i>.\n\n'
                                              '❗️<b>ВАЖНО</b>❗ После выбора товара на сайте mp-keshbek.ru Вам придет в данный бот'
                                              ' уведомление с дальнейшими инструкциями.\n\n'
                                              '<b>🛍ПОРА ЗА ПОКУПКАМИ🛍</b>',
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=base_inline_kb_post_auth(quan_products_accept=quan_products_accept,
                                                                                         quan_products_not_accept=len(new_product)))
        except:
            media = InputMediaPhoto(media=photo,
                                    caption='<i>Если по каким-то причинам авторизация на wb будет'
                                            ' сброшена, бот вас об этом уведомит</i>.☺️\n\n'
                                            '❗️<b>ВАЖНО</b>❗ После выбора товара на сайте mp-keshbek.ru Вам придет в данный бот'
                                            ' уведомление с дальнейшими инструкциями.\n\n'
                                            '<b>🛍ПОРА ЗА ПОКУПКАМИ🛍</b>',
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=base_inline_kb_post_auth(quan_products_accept=quan_products_accept,
                                                                                         quan_products_not_accept=len(
                                                                                             new_product)))
        await insert_msd_products(user_id=user_id,
                                  message_id=message.message_id)

    else:

        await delete_message(chat_id=user_id,
                             list_message_id=messages + messages_2 + messages_3,
                             bot=bot)
        await delete_message_id_registration(user_id=user_id)
        await delete_edit_start_auth(user_id=user_id)
        await delete_edit_wb_auth(user_id=user_id)
        photo = FSInputFile(path="base_photo/good_auth.png")
        message = await bot.send_photo(chat_id=user_id,
                                       caption='<i>Если по каким-то причинам авторизация на wb будет'
                                               ' сброшена, бот вас об этом уведомит</i>.\n\n'
                                               '❗️<b>ВАЖНО</b>❗ После выбора товара на сайте mp-keshbek.ru Вам придет в данный бот'
                                               ' уведомление с дальнейшими инструкциями.\n\n'
                                               '<b>🛍ПОРА ЗА ПОКУПКАМИ🛍</b>',
                                       parse_mode="HTML",
                                       photo=photo,
                                       reply_markup=base_inline_kb_post_auth(quan_products_accept=quan_products_accept,
                                                                             quan_products_not_accept=len(new_product)))
        await insert_msd_products(user_id=user_id,
                                  message_id=message.message_id)

    await state_clear_auth(user_id=user_id)
    await delete_sms_cp(user_id=user_id)
    await bot.session.close()


async def new_product_send_users(user_id):#добавить edit
    bot = Bot(token=TG_TOKEN, session=None)
    messages_4 = await select_edit_products(user_id=user_id)
    new_product = await check_new_products(user_id=user_id)
    last_new_product = new_product[0]
    #print(new_product, "#################################################################################################")
    photo = last_new_product[1]
    order_id = last_new_product[2]
    article = last_new_product[3]
    page = last_new_product[4]
    position = last_new_product[5]
    wb_search_url = last_new_product[6]
    quan_products_accept = select_accept_orders(chat_id=user_id)
    if quan_products_accept == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept)

    if len(new_product) == 1:
        try:
            print(1)
            photo = URLInputFile(photo)
            print(2)
            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                             f'<b>Артикул:</b> {article}\n'
                                             f'<b>Карточка товара на странице:</b> {page}\n'
                                             f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                             f"<b>Ссылка для поиска товара:</b> <a href='{wb_search_url}'>ссылка</a>\n\n"
                                             f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                             f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                             f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                                   user_id=user_id,
                                                                                   order_id=order_id))
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
        except Exception as e:
            print(e)

            photo = URLInputFile(photo)

            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                    f'<b>Артикул:</b> {article}\n'
                                                    f'<b>Карточка товара на странице:</b> {page}\n'
                                                    f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                    f"<b>Ссылка для поиска товара:</b> <a href='{wb_search_url}'>ссылка</a>\n\n"
                                                    f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                    f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                    f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                           parse_mode="HTML",
                                           reply_markup=kb_check_order_one(quan_products_accept=quan_products_accept,
                                                                           user_id=user_id,
                                                                           order_id=order_id))
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)

    else:
        try:
            quantity_products = len(new_product)

            photo = URLInputFile(photo)

            media = InputMediaPhoto(media=photo,
                                    caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                             f'<b>Артикул:</b> {article}\n'
                                             f'<b>Карточка товара на странице:</b> {page}\n'
                                             f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                             f"<b>Ссылка для поиска товара:</b> <a href='{wb_search_url}'>ссылка</a>\n\n"
                                             f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                             f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                             f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                                    user_id=user_id,
                                                                                    order_id=order_id,
                                                                                    inline_page=f"1/{quantity_products}"))
            await new_insert_or_update_page_products(user_id=user_id)
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
        except Exception as e:

            quantity_products = len(new_product)

            photo = URLInputFile(photo)

            message = await bot.send_photo(chat_id=user_id,
                                           photo=photo,
                                           reply_markup=kb_check_order_many(quan_products_accept=quan_products_accept,
                                                                            user_id=user_id,
                                                                            order_id=order_id,
                                                                            inline_page=f"1/{quantity_products}"),
                                           caption=(f'<b>Номер вашего заказа:</b> {order_id}\n'
                                                    f'<b>Артикул:</b> {article}\n'
                                                    f'<b>Карточка товара на странице:</b> {page}\n'
                                                    f'<b>Примерный порядковый номер на странице:</b> {position}\n'
                                                    f"<b>Ссылка для поиска товара:</b> <a href='{wb_search_url}'>ссылка</a>\n\n"
                                                    f'<b>Совет:</b> Обратите внимание, что фото товара может отличаться от реального вида.'
                                                    f'Проверьте товар по артикулу и постарайтесь приобрести его как можно быстрее.\n'
                                                    f'<i>Если вы не нашли товар по ссылке, попробуйте поискать его без указания бренда!</i>'),
                                           parse_mode="HTML")
            await new_insert_or_update_page_products(user_id=user_id)
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)

    news = await bot.send_message(chat_id=user_id,
                                  text="❗️У ВАС НОВЫЙ ЗАКАЗ❗️")
    await asyncio.sleep(10)
    await bot.delete_message(chat_id=user_id,
                             message_id=news.message_id)
    await bot.session.close()


async def restart_auth(user_id):
    print(user_id,  type(user_id))
    bot = Bot(token=TG_TOKEN, session=None)
    messages_4 = await select_edit_products(user_id=user_id)
    await state_clear_auth(int(user_id))
    await delete_sms_cp(int(user_id))
    try:
        try:
            photo = FSInputFile("base_photo/resend_auth.png")
            media = InputMediaPhoto(media=photo,
                                    caption=(f'Cброшена авторизация на WB.\n'
                                             f'Авторизуйтесь пожалуйста заново☺️'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)
        except Exception as e:
            print(e)
            photo = FSInputFile("base_photo/resend_auth.png")
            media = InputMediaPhoto(media=photo,
                                    caption=(f'Cброшена авторизация на WB☺️.\n'
                                             f'Авторизуйтесь пожалуйста заново☺️'),
                                    parse_mode="HTML")
            message = await bot.edit_message_media(chat_id=user_id,
                                                   media=media,
                                                   message_id=messages_4,
                                                   reply_markup=start_kb())
            await insert_msd_products(user_id=user_id,
                                      message_id=message.message_id)

    except Exception as e:
        print(e)
        photo = FSInputFile("base_photo/resend_auth.png")
        message = await bot.send_photo(chat_id=user_id,
                                       photo=photo,
                                       caption=(f'Cброшена авторизация на WB.\n'
                                                f'Авторизуйтесь пожалуйста заново☺️'),
                                       parse_mode="HTML",
                                       reply_markup=start_kb())
        await insert_msd_products(user_id=user_id,
                                  message_id=message.message_id)
    clear_db_auth_user(str(user_id))
    await bot.session.close()








# user_id, order_id, article, page, position, wb_search_url

# order_tg_message = (f'<b>Номер вашего заказа:</b> {order_id}\n'
#                    f'<b>Артикул:</b> {link_product_id}\n'
#                    f'<b>Карточка товара на странице:</b> {page}\n'
#                    f'<b>Примерный порядковый номер на страницк:</b> {position}\n\n'
#                    f'<b>Ссылка для поиска товара:</b> <a href={wb_search_url}>ссылка</a>\n\n'
#                    f'<i>Если вы не нашли товар на странице по ссылке, попробуйте найти его'
#                    f' на соседних страницах</i>')

# bot.send_message(chat_id, base_order_tg_message,  parse_mode="HTML")
# bot.send_photo(chat_id, image_link, caption=order_tg_message)






