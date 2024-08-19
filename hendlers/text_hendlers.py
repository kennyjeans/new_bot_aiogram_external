import asyncio
import psycopg2
from aiogram import Router, F, types, Bot
from aiogram.filters import StateFilter
from fake_useragent import UserAgent
from aiogram.types import FSInputFile, InputMediaPhoto
from state_bot import StateEmail, StatePhone, StateNewAdmin, StateDelAdmin
from aiogram.fsm.context import FSMContext
from utils import get_db_connection
from keyboards.inline_kb import shopping, start_kb, cancel_new_admin, base_inline_kb_post_auth
from keyboards.inline_kb import cancel
from dop_func_bot.dop_func import try_write_new_tg_user, check_free_selenium, delete_message
from data_base.aiosqlite_func import (select_registration, insert_registration_data,
                                      insert_edit_start_auth, delete_message_id_registration,
                                      insert_shopping, delete_edit_start_auth, select_edit_start_auth,
                                      state_clear_auth, set_state_auth, check_state, select_admins,
                                      new_admin, select_cp_sms, update_sms_quan, update_cp_quan, insert_edit_wb_auth,
                                      select_edit_products, insert_msd_products, check_new_products, delete_admin)
from data_base.pg_db_func import write_captcha, write_sms_code, select_accept_orders

text_router = Router()
ua = UserAgent(platforms='pc', os=["windows", "macos"], browsers='chrome')


@text_router.message(F.text, StateFilter(StateEmail.email_state))
async def email_text(msd: types.Message, state: FSMContext, bot: Bot):
    email = msd.text.replace(" ", '')
    message = await insert_registration_data(user_id=msd.from_user.id,
                                             message_id=msd.message_id)
    quan_products_accept = select_accept_orders(chat_id=msd.from_user.id)
    if quan_products_accept == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept)
    watch = 0
    conn = get_db_connection()
    cur = conn.cursor()
    if "@" in email:
        check_email_list = email.split("@")
        if len(check_email_list[0]) >= 1 and check_email_list[1]:
            cur.execute('select wp_email, is_verified, chat_id from auth_user where wp_email = %(email)s',
                        {'email': email})
            user_email = cur.fetchone()

            if not user_email:
                #анимация проверки авторизации пользователя (требуется так как запись в бд происходит с time.sleep(60))
                check_auth = await msd.answer("Идет проверка авторизации на сайте...⏳")
                for i in range(15):
                    if i % 5 == 0:
                        cur.execute('select wp_email, is_verified, chat_id from auth_user where wp_email = %(email)s',
                                    {'email': email})
                        user_email = cur.fetchone()
                        if user_email:
                            if user_email[1] is not None:
                                new_product = await check_new_products(user_id=msd.from_user.id)
                                messages = await select_registration(user_id=msd.from_user.id)
                                messages_4 = await select_edit_products(user_id=msd.from_user.id)
                                try:
                                    await delete_message(chat_id=msd.from_user.id,
                                                         list_message_id=messages + [(check_auth.message_id,)],
                                                         bot=bot)

                                    photo = FSInputFile(path="base_photo/basic_menu.png")
                                    media = InputMediaPhoto(media=photo,
                                                            caption=('ВЫ УЖЕ АВТОРИЗОВАНЫ😊\n\n'
                                                                     '🛍Время покупок на нашем сайте:<a href="https://mp-keshbek.ru/">mp-keshbek.ru</a>\n'
                                                                     '<b>За кэшбэком возаращайтесь СЮДА</b>'),
                                                            parse_mode="HTML")
                                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                                           media=media,
                                                                           message_id=messages_4,
                                                                           reply_markup=base_inline_kb_post_auth(
                                                                               quan_products_accept=quan_products_accept,
                                                                               quan_products_not_accept=len(new_product)))
                                    await insert_msd_products(user_id=msd.from_user.id,
                                                              message_id=message.message_id)
                                    conn.close()
                                    await state.clear()
                                except:
                                    await delete_message(chat_id=msd.from_user.id,
                                                         list_message_id=messages + [(check_auth.message_id,)],
                                                         bot=bot)

                                    photo = FSInputFile(path="base_photo/basic_menu.png")
                                    media = InputMediaPhoto(media=photo,
                                                            caption=('ВЫ УЖЕ АВТОРИЗОВАНЫ😊\n\n'
                                                                     '🛍Время покупок на нашем сайт🛍е:<a href="https://mp-keshbek.ru/">mp-keshbek.ru</a>\n'
                                                                     '<b>☺️За кэшбэком возаращайтесь СЮДА</b>'),
                                                            parse_mode="HTML")
                                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                                           media=media,
                                                                           message_id=messages_4,
                                                                           reply_markup=base_inline_kb_post_auth(
                                                                               quan_products_accept=quan_products_accept,
                                                                               quan_products_not_accept=len(new_product)))

                                    await insert_msd_products(user_id=msd.from_user.id,
                                                              message_id=message.message_id)
                                    conn.close()
                                    await state.clear()
                                return

                            if isinstance(user_email[2], int) and msd.from_user.id != int(user_email[2]):
                                messages = await select_registration(user_id=msd.from_user.id)
                                messages_4 = await select_edit_products(user_id=msd.from_user.id)
                                await delete_message(chat_id=msd.from_user.id,
                                                     list_message_id=messages + [(check_auth.message_id,)],
                                                     bot=bot)
                                await delete_message_id_registration(user_id=msd.from_user.id)
                                try:
                                    photo = FSInputFile(path="base_photo/email_error.png")
                                    media = InputMediaPhoto(media=photo,
                                                            caption=(f'☝️Аккаунт с такой почтой: {email}\n'
                                                                     f'Привязан к другому телеграм аккаунту\n\n'
                                                                     f'<b>Для начала работы требуется авторизация на 2-ух сайтах:</b>\n'
                                                                     '1. mp-keshbek.ru\n'
                                                                     '2. WB (через данный бот)'),
                                                            parse_mode="HTML")
                                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                                           media=media,
                                                                           message_id=messages_4,
                                                                           reply_markup=start_kb())

                                    await insert_msd_products(user_id=msd.from_user.id,
                                                              message_id=message.message_id)
                                except:
                                    photo = FSInputFile(path="base_photo/email_error.png")
                                    media = InputMediaPhoto(media=photo,
                                                            caption=(f'☝️Аккаунт с такой почтой: {email}\n'
                                                                     f'Привязан к другому телеграм аккаунту\n\n'
                                                                     f'☺️<b>Для начала работы требуется авторизация на 2-ух сайтах:</b>\n'
                                                                     '1. mp-keshbek.ru\n'
                                                                     '2. WB (через данный бот)'),
                                                            parse_mode="HTML")
                                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                                           media=media,
                                                                           message_id=messages_4,
                                                                           reply_markup=start_kb())

                                    await insert_msd_products(user_id=msd.from_user.id,
                                                              message_id=message.message_id)

                                conn.close()
                                await state.clear()
                                return
                            break
                    elif i == 14:
                        messages = await select_registration(user_id=msd.from_user.id)
                        messages_4 = await select_edit_products(user_id=msd.from_user.id)
                        await delete_message(chat_id=msd.from_user.id,
                                             list_message_id=messages + [(check_auth.message_id,)],
                                             bot=bot)
                        await delete_message_id_registration(user_id=msd.from_user.id)
                        try:
                            photo = FSInputFile(path="base_photo/email_error_input.png")
                            media = InputMediaPhoto(media=photo,
                                                    caption=(f'😑<b>Пользователь с такой {email} почтой не зарегистрирован на сайте mp-keshbek.ru</b>\n\n'
                                                              '<b>Для начала работы требуется авторизация на 2-ух сайтах:</b>\n'
                                                              '1. mp-keshbek.ru\n'
                                                              '2. WB (через данный бот)'),
                                                    parse_mode="HTML")
                            message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                                   media=media,
                                                                   message_id=messages_4,
                                                                   reply_markup=start_kb())

                            await insert_msd_products(user_id=msd.from_user.id,
                                                      message_id=message.message_id)
                        except:
                            photo = FSInputFile(path="base_photo/email_error_input.png")
                            media = InputMediaPhoto(media=photo,
                                                    caption=(f'😑<b>Пользователь с такой {email} почтой не зарегистрирован на сайте mp-keshbek.ru</b>\n\n'
                                                             '<b☺️>Для начала работы требуется авторизация на 2-ух сайтах:</b>\n'
                                                             '1. mp-keshbek.ru\n'
                                                             '2. WB (через данный бот)'),
                                                    parse_mode="HTML")
                            message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                                   media=media,
                                                                   message_id=messages_4,
                                                                   reply_markup=start_kb())

                            await insert_msd_products(user_id=msd.from_user.id,
                                                      message_id=message.message_id)

                        conn.close()
                        await state.clear()
                        return
                    watch += 1

                    await asyncio.sleep(2)
                    if watch == 1:
                        check_auth = await bot.edit_message_text(chat_id=msd.from_user.id,
                                                                 text="Идет проверка авторизации на сайте...⏳⏳",
                                                                 message_id=check_auth.message_id)
                    elif watch == 2:
                        check_auth = await bot.edit_message_text(chat_id=msd.from_user.id,
                                                                 text="Идет проверка авторизации на сайте...⏳⏳⏳",
                                                                 message_id=check_auth.message_id)
                    elif watch == 3:
                        check_auth = await bot.edit_message_text(chat_id=msd.from_user.id,
                                                                 text="Идет проверка авторизации на сайте...⏳",
                                                                 message_id=check_auth.message_id)
                        watch -= 3

            elif user_email[1]:
                new_product = await check_new_products(user_id=msd.from_user.id)
                messages = await select_registration(user_id=msd.from_user.id)
                messages_4 = await select_edit_products(user_id=msd.from_user.id)
                try:
                    await delete_message(chat_id=msd.from_user.id,
                                         list_message_id=messages,
                                         bot=bot)

                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=('ВЫ УЖЕ АВТОРИЗОВАНЫ😊\n\n'
                                                     '🛍Время покупок на нашем сайте:<a href="https://mp-keshbek.ru/">mp-keshbek.ru</a>\n'
                                                     '<b>За кэшбэком возаращайтесь СЮДА</b>'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                    conn.close()
                    await state.clear()
                except:
                    await delete_message(chat_id=msd.from_user.id,
                                         list_message_id=messages,
                                         bot=bot)

                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=('ВЫ УЖЕ АВТОРИЗОВАНЫ😊\n\n'
                                                     '🛍Время покупок на нашем сайт🛍е:<a href="https://mp-keshbek.ru/">mp-keshbek.ru</a>\n'
                                                     '<b>За кэшбэком возаращайтесь СЮДА☺️</b>'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                    conn.close()
                    await state.clear()
                return

            elif isinstance(user_email[2], int) and msd.from_user.id != int(user_email[2]):
                messages = await select_registration(user_id=msd.from_user.id)
                messages_4 = await select_edit_products(user_id=msd.from_user.id)
                await delete_message(chat_id=msd.from_user.id,
                                     list_message_id=messages,
                                     bot=bot)
                await delete_message_id_registration(user_id=msd.from_user.id)
                try:
                    photo = FSInputFile(path="base_photo/auth.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(
                                                f'☝️Аккаунт с такой почтой: {email}\n'
                                                 f'Привязан к другому телеграм аккаунту\n\n'
                                                 'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                                 '1. mp-keshbek.ru\n'
                                                 '2. WB (через данный бот)'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=start_kb())

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                except:
                    photo = FSInputFile(path="base_photo/auth.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(
                                                f'☝️Аккаунт с такой почтой: {email}\n'
                                                 f'Привязан к другому телеграм аккаунту\n\n'
                                                 '☺️Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                                 '1. mp-keshbek.ru\n'
                                                 '2. WB (через данный бот)'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=start_kb())

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)

                conn.close()
                await state.clear()
                return

            else:
                try:
                    print(email, f"{msd.from_user.id}")
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("""UPDATE auth_user SET chat_id = %(chat_id)s WHERE wp_email = %(email)s""",
                                {'chat_id': f"{msd.from_user.id}",
                                 'email': email})
                    conn.commit()
                    conn.close()
                except psycopg2.Error as e:
                    print(e)
                message = await msd.answer(text=("<b>Введите номер телефона</b>:\n\n"
                                                 "<b>Пример для России:</b> +79995553322\n"),
                                           reply_markup=cancel(),
                                           parse_mode="HTML")# pass

                await insert_registration_data(user_id=msd.from_user.id,
                                               message_id=message.message_id)
                await state.set_state(StatePhone.phone_state)

    else:
        text_message = ('☹️Почтовый адресс введен некорректно\n\n'
                        '<b>Введите почту:</b>\n'
                        '<b>Пример:</b> pepa@example.ru')
        message = await msd.answer(text=text_message,
                                   reply_markup=cancel(),
                                   parse_mode="HTML")  # pass
        await insert_registration_data(user_id=msd.from_user.id,
                                       message_id=message.message_id)
        return


@text_router.message(F.text, StateFilter(StatePhone.phone_state))
async def email_text(msd: types.Message, state: FSMContext, bot: Bot):
    phone = msd.text

    await insert_registration_data(user_id=msd.from_user.id,
                                   message_id=msd.message_id)

    quan_products_accept = select_accept_orders(chat_id=msd.from_user.id)
    if quan_products_accept == []:
        quan_products_accept = 0
    else:
        quan_products_accept = len(quan_products_accept)
    if phone[0:4] == '+375' and len(phone) == 13:
        pass
    elif not phone or phone[0:2] != '+7' or len(phone) != 12:
        text_message = ('☹️Номер телефона введен некорректно\n\n'
                        '<b>Введите номер телефона:</b>\n'
                        '<b>Пример для России:</b> +79995553322\n')

        message = await msd.answer(text=text_message,
                                   reply_markup=cancel(),
                                   parse_mode="HTML")# pass
        await insert_registration_data(user_id=msd.from_user.id,
                                       message_id=message.message_id)
        return
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""UPDATE auth_user SET phone_number = %(phone_number)s WHERE chat_id = %(chat_id)s""",
                    {"phone_number": phone,
                     "chat_id": f'{msd.from_user.id}'})
        conn.commit()
        try:
            cur.execute("SELECT wp_email FROM auth_user WHERE chat_id = %(user_id)s",
                        {"user_id": f"{msd.from_user.id}"})
            email = cur.fetchone()[0]
            situation_status = check_free_selenium(msd.from_user.id, phone, email)
        except Exception as e:
            print(e, phone, msd.text, '3232')
            conn.close()
            await state.clear()
            return

        if isinstance(situation_status, int):

            try:
                print(email, "#########")
                is_success = try_write_new_tg_user(msd.from_user.id, phone, situation_status, email)
                print(is_success)
            except:
                print(phone, msd.text)
                conn.close()
                await state.clear()
                return

            if is_success is False:
                text_message = ('<b>На данный момент авторизация не возможна</b>☹️\n'
                                'Бот уведомил поддержку о данной проблеме.\n\n')#закончились прокси
                admins = await select_admins()
                for admin in admins:
                    try:
                        await bot.send_message(chat_id=admin[0],
                                               text=("У данного пользователя возникли проблемы"
                                                     " с авторизацией из-за отсутствия proxy\n\n"
                                                     "Данные пользовтеля:\n"
                                                     f"user_name: {msd.from_user.username}\n"
                                                     f"first_name: {msd.from_user.first_name}\n"
                                                     f"last_name: {msd.from_user.last_name}\n"
                                                     f"user_id: {msd.from_user.id}"))
                    except Exception as e:
                        print(f"Для данного администратора рассылка не сработала {msd.from_user.id}", e)

                messages = await select_registration(user_id=msd.from_user.id)
                messages_4 = await select_edit_products(user_id=msd.from_user.id)
                await delete_message(chat_id=msd.from_user.id,
                                     list_message_id=messages,
                                     bot=bot)
                await delete_message_id_registration(user_id=msd.from_user.id)
                try:
                    photo = FSInputFile(path="base_photo/auth.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(text_message +
                                                '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                                 'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                                 '1. mp-keshbek.ru\n'
                                                 '2. WB (через данный бот)'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=start_kb())

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                except:
                    photo = FSInputFile(path="base_photo/auth.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(
                                                 '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                                 'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                                 '1. mp-keshbek.ru\n'
                                                 '2. WB (через данный бот)'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=start_kb())

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)

                await state.clear()
                cur.execute("""UPDATE auth_user SET chat_id = %(user_id)s, phone_number = %(phone)s
                               WHERE chat_id = %(chat_id)s""",
                            {"chat_id": f'{msd.from_user.id}',
                             "user_id": None,
                             "phone": None}) #зачищаем заполненные данные что б при повторной регистрации не произошли ошибки
                conn.commit()
                cur.close()
                await state.clear()
            else:
                text_message = 'Начат процесс авторизации...⏳' #можно сделать через edit
                message = await msd.answer(text=text_message)
                await insert_edit_start_auth(user_id=msd.from_user.id,
                                             message_id=message.message_id)
                await state.clear()
        else:
            situation = situation_status
            if situation == "1":
                new_product = await check_new_products(user_id=msd.from_user.id)
                messages = await select_registration(user_id=msd.from_user.id)
                messages_4 = await select_edit_products(user_id=msd.from_user.id)
                try:
                    await delete_message(chat_id=msd.from_user.id,
                                         list_message_id=messages,
                                         bot=bot)

                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=('ВЫ УЖЕ АВТОРИЗОВАНЫ😊\n\n'
                                                     '🛍Время покупок на нашем сайте:<a href="https://mp-keshbek.ru/">mp-keshbek.ru</a>\n'
                                                     '<b>За кэшбэком возаращайтесь СЮДА</b>'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))
                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                    conn.close()
                    await state.clear()
                except:
                    await delete_message(chat_id=msd.from_user.id,
                                         list_message_id=messages,
                                         bot=bot)

                    photo = FSInputFile(path="base_photo/basic_menu.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=('ВЫ УЖЕ АВТОРИЗОВАНЫ😊\n\n'
                                                     '🛍Время покупок на нашем сайт🛍е:<a href="https://mp-keshbek.ru/">mp-keshbek.ru</a>\n'
                                                     '<b>За кэшбэком возаращайтесь СЮДА☺️</b>'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=base_inline_kb_post_auth(
                                                               quan_products_accept=quan_products_accept,
                                                               quan_products_not_accept=len(new_product)))

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                    conn.close()
                    await state.clear()
            elif situation == "2":
                messages = await select_edit_start_auth(user_id=msd.from_user.id)
                await delete_message(chat_id=msd.from_user.id,
                                     list_message_id=messages,
                                     bot=bot)
                await delete_edit_start_auth(user_id=msd.from_user.id)
                message = await msd.answer(text=("У вас уже начат процесс авторизации.\nНужно немного подождать...⏳"),
                                           parse_mode="HTML")
                await insert_edit_start_auth(user_id=msd.from_user.id,
                                             message_id=message.message_id)
                await state.clear()
            elif situation == "3":
                try:
                    messages = await select_registration(user_id=msd.from_user.id)
                    await delete_message(chat_id=msd.from_user.id,
                                         list_message_id=messages,
                                         bot=bot)
                    messages_4 = await select_edit_products(user_id=msd.from_user.id)
                    photo = FSInputFile(path="base_photo/auth.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(
                                                '<b>☹️ОБРАЗОВАЛАСЬ НЕБОЛЬШАЯ ОЧЕРЕДЬ НА РЕГИСТРАЦИЮ☹️</b>\n\n'
                                                 '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                                 'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                                 '1. mp-keshbek.ru\n'
                                                 '2. WB (через данный бот)'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=start_kb())

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)
                except:
                    messages_4 = await select_edit_products(user_id=msd.from_user.id)
                    messages = await select_registration(user_id=msd.from_user.id)
                    await delete_message(chat_id=msd.from_user.id,
                                         list_message_id=messages,
                                         bot=bot)
                    photo = FSInputFile(path="base_photo/auth.png")
                    media = InputMediaPhoto(media=photo,
                                            caption=(
                                                 '<b>☹️ОБРАЗОВАЛАСЬ НЕБОЛЬШАЯ ОЧЕРЕДЬ НА РЕГИСТРАЦИЮ☹️</b>\n\n'
                                                 '<b>🙏ПОПРОБУЙТЕ ЧУТЬ ПОЗЖЕ🙏</b>\n'
                                                 'Для начала работы требуется авторизация на 2-ух сайтах:\n'
                                                 '1. mp-keshbek.ru\n'
                                                 '2. WB (через данный бот)'),
                                            parse_mode="HTML")
                    message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                           media=media,
                                                           message_id=messages_4,
                                                           reply_markup=start_kb())

                    await insert_msd_products(user_id=msd.from_user.id,
                                              message_id=message.message_id)

                await state.clear()
            else:
                pass
        conn.close()
        print(phone, msd.from_user.id)


@text_router.message(F.text(), StateFilter(StateNewAdmin.new_admin_state))
async def new_admin_text(msd: types.Message, state: FSMContext):
    data = msd.text
    data = data.replace(" ", '')
    if ',' in data and data.count(',') == 1:
        data = data.split(',')
        try:
            user_id = int(data[0])
            name = str(data[1])
            await new_admin(user_id=user_id,
                            name=name)
            await state.clear()
        except Exception as e:
            await msd.answer(text="Данные нового администратора введены неверно:\n\n"
                                  f"ОШИБКА {e} "
                                  "Пример: 72336272, AlenaS\n"
                                  "Где 1 значение это user_id новго администратора (можно получить если новый администратор"
                                  " введет в боте команду /user_id)\n"
                                  "А второе имя нового администратора (Не обязательно @username)",
                             reply_markup=cancel_new_admin())
    else:
        await msd.answer(text="Данные нового администратора введены неверно:\n\n"
                              "Пример: 72336272, AlenaS\n"
                              "Где 1 значение это user_id новго администратора (можно получить если новый администратор"
                              " введет в боте команду /user_id)\n"
                              "А второе имя нового администратора (Не обязательно @username)",
                         reply_markup=cancel_new_admin())


@text_router.message(F.text(), StateFilter(StateDelAdmin.del_admin_state))
async def del_admin_text(msd: types.Message, state: FSMContext):
    data = msd.text
    data = data.replace(" ", '')
    await delete_admin(user_id=msd.from_user.id)
    await state.clear()



#обязательно должно быть последним
@text_router.message(F.text)
async def get_captcha(msd: types.Message, bot: Bot):
    """
    Обрабатывает команду для получения капчи.
    """
    state_auth = await check_state(msd.from_user.id)
    print(state_auth)
    if state_auth == "cp":
        await update_cp_quan(msd.from_user.id)
        captcha = msd.text
        await insert_registration_data(user_id=msd.from_user.id,
                                       message_id=msd.message_id)
        try:
            message = await msd.answer(text="Капча получена, идет проверка...⌛️")
            await insert_edit_wb_auth(user_id=msd.from_user.id,
                                      message_id=message.message_id)
            captcha_iteration = await select_cp_sms(user_id=msd.from_user.id, find_is="cp")
            write_captcha(chat_id=msd.chat.id,
                          captcha=captcha.replace(" ", ''),
                          captcha_iteration=captcha_iteration)
            await state_clear_auth(msd.from_user.id)
        except Exception as e:
            print(f"Ошибка у пользователя {msd.from_user.id} при вводе капчи в бд ", e)

    elif state_auth == "sms":
        code = msd.text.replace(" ", "")
        try:
            int(code)
            check_code = 1
        except:
            check_code = 0

        if check_code == 1:
            if len(msd.text) == 6:
                message = await msd.answer(text="Код получен, идет проверка...⌛️")
                await insert_edit_wb_auth(user_id=msd.from_user.id,
                                          message_id=message.message_id)
                await insert_registration_data(user_id=msd.from_user.id,
                                               message_id=msd.message_id)
                await update_sms_quan(msd.from_user.id)
                sms_iteration = await select_cp_sms(user_id=msd.from_user.id, find_is="sms")
                write_sms_code(chat_id=msd.from_user.id,
                               sms_code=msd.text.replace(" ", ''),
                               code_iteration=sms_iteration)
                await state_clear_auth(msd.from_user.id)
            else:
                await insert_registration_data(user_id=msd.from_user.id,
                                               message_id=msd.message_id)
                message = await msd.answer(text="<b>☝️КОД ВВЕДЕН НЕ КОРРЕКТНО</b>☝️\n"
                                                "Код должен состоять из 6 цифр\n\n"
                                                "😌<b>Введите код повторно</b>😌",
                                           parse_mode="HTML")
                await insert_registration_data(user_id=msd.from_user.id,
                                               message_id=message.message_id)
        else:
            await insert_registration_data(user_id=msd.from_user.id,
                                           message_id=msd.message_id)
            message = await msd.answer(text="<b>☝️КОД ВВЕДЕН НЕ КОРРЕКТНО</b>☝️\n"
                                                "Код должен состоять из 6 цифр\n\n"
                                                "😌<b>Введите код повторно</b>😌",
                                       parse_mode="HTML")
            await insert_registration_data(user_id=msd.from_user.id,
                                           message_id=message.message_id)

    else:
        await bot.delete_message(chat_id=msd.from_user.id,
                                 message_id=msd.message_id)









