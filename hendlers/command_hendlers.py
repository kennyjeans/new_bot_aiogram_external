import asyncio

from aiogram import Router, types, Bot
from aiogram.filters import Command
from keyboards.inline_kb import start_kb, cancel_new_admin, kb_check_order_many, cancel_del_admin
from data_base.aiosqlite_func import insert_registration_data, insert_start_sms_cp, insert_msd_products, \
    select_edit_products, state_clear_auth, check_new_products, select_page_product
from data_base.aiosqlite_func import check_admin
from state_bot import StateNewAdmin, StateDelAdmin
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile, InputMediaPhoto, URLInputFile

command_router = Router()


@command_router.message(Command("start"))
async def start_command(msd: types.Message, bot: Bot):
    await bot.delete_message(chat_id=msd.from_user.id,
                             message_id=msd.message_id)
    messages_4 = await select_edit_products(user_id=msd.from_user.id)
    photo = FSInputFile("base_photo/auth.png")
    if messages_4 == None:
        message = await bot.send_photo(chat_id=msd.from_user.id,
                                       caption=("Привет от mp-keshbek👋\n\n"
                                                "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                                "1. mp-keshbek.ru\n"
                                                "2. WildBerries (через данный бот)"),
                                       reply_markup=start_kb(),
                                       photo=photo)
        await insert_msd_products(user_id=msd.from_user.id,
                                  message_id=message.message_id)
        await state_clear_auth(user_id=msd.from_user.id)
    else:
        try:
            try:
                media = InputMediaPhoto(media=photo,
                                        caption=("Привет от mp-keshbek👋\n\n"
                                                 "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                                 "1. mp-keshbek.ru\n"
                                                 "2. WildBerries (через данный бот)"),
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=start_kb())
                await insert_msd_products(user_id=msd.from_user.id,
                                          message_id=message.message_id)
                await state_clear_auth(user_id=msd.from_user.id)
            except:
                media = InputMediaPhoto(media=photo,
                                        caption=("👋Привет от mp-keshbek👋\n\n"
                                                 "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                                 "1. mp-keshbek.ru\n"
                                                 "2. WildBerries (через данный бот)"),
                                        parse_mode="HTML")
                message = await bot.edit_message_media(chat_id=msd.from_user.id,
                                                       media=media,
                                                       message_id=messages_4,
                                                       reply_markup=start_kb())
                await insert_msd_products(user_id=msd.from_user.id,
                                          message_id=message.message_id)
                await state_clear_auth(user_id=msd.from_user.id)
        except:
            message = await bot.send_photo(chat_id=msd.from_user.id,
                                           caption=("Привет от mp-keshbek👋\n\n"
                                                    "Для начала работы требуется авторизация на 2-ух сайтах:\n"
                                                    "1. mp-keshbek.ru\n"
                                                    "2. WildBerries (через данный бот)"),
                                           reply_markup=start_kb(),
                                           photo=photo)
            await insert_msd_products(user_id=msd.from_user.id,
                                      message_id=message.message_id)
            await state_clear_auth(user_id=msd.from_user.id)

    await insert_start_sms_cp(msd.from_user.id)


@command_router.message(Command("new_admin"), StateFilter(None))
async def new_admin(msd: types.Message, bot: Bot, state: FSMContext):
    data = await check_admin(msd.from_user.id) #bool
    if data is False:
        message = await bot.send_sticker(chat_id=msd.from_user.id,
                                         sticker="CAACAgIAAxkBAAELJNFln-HNLHEbnev_OToMqQWRtr"
                                                 "V0VQAC6xQAAqPTsEmXDa8Z4Dsg8DQE")
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=msd.from_user.id,
                                 message_id=message.message_id)

    else:
        await msd.answer(text="Введите данные в таком формате:\n\n"
                              "Пример: 72336272, AlenaS\n"
                              "Где 1 значение это user_id новго администратора (можно получить если новый администратор"
                              " введет в боте команду /user_id)\n"
                              "А второе имя нового администратора (Не обязательно @username)",
                         reply_markup=cancel_new_admin())
        await state.set_state(StateNewAdmin.new_admin_state)


@command_router.message(Command("user_id"))
async def user_id(msd: types.Message):
    await msd.answer(text=str(msd.from_user.id))


@command_router.message(Command("delete_admin"), StateFilter(None))
async def new_admin(msd: types.Message, bot: Bot, state: FSMContext):
    data = await check_admin(msd.from_user.id) #bool
    if data is False:
        message = await bot.send_sticker(chat_id=msd.from_user.id,
                                         sticker="CAACAgIAAxkBAAELJNFln-HNLHEbnev_OToMqQWRtr"
                                                 "V0VQAC6xQAAqPTsEmXDa8Z4Dsg8DQE")
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=msd.from_user.id,
                                 message_id=message.message_id)

    else:
        await msd.answer(text="Введите данные в таком формате:\n\n"
                              "Пример: 72336272\n"
                              "Где значение это user_id администратора, которого нужно удалить (можно получить если новый администратор"
                              " введет в боте команду /user_id)\n",
                         reply_markup=cancel_del_admin())
        await state.set_state(StateDelAdmin.del_admin_state)









