from aiogram import Dispatcher, Bot
import asyncio
from settings import TG_TOKEN
from aiogram.methods import DeleteWebhook
from aiogram.fsm.storage.memory import MemoryStorage
from hendlers.command_hendlers import command_router
from hendlers.text_hendlers import text_router
from hendlers.callback_hendlers import cb_router
from dop_func_bot.dop_func import router_storage


def on_startup():
    print('Бот запущен')


def shutdown_func():
    print("Бот выключен")


async def main():
    bot = Bot(TG_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(cb_router,
                       command_router,
                       router_storage,
                       text_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(shutdown_func)

    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())