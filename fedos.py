import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command


from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

reply_keyboard = [[KeyboardButton(text='/create'), KeyboardButton(text='/help')],
                  [KeyboardButton(text='/check')],
                  [KeyboardButton(text="/stop")]]

kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)


dp = Dispatcher() # создаем маршрутизатор
BOT_TOKEN = "7309765684:AAEYKRlw7HRhD7ypk3zwKzeSzQSHVcaPoKo"


async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


@dp.message(Command('start'))
async def start(message: types.Message):
    await message.reply("Привет! Я ДНД бот! Давай создадим персонажа!\n"
                        "/create - создать нового персонажа\n"
                        "/check - просмотреть созданных персонажей\n"
                        "/help - справочник",reply_markup=kb)


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока.", reply_markup=ReplyKeyboardRemove())


@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply("Я ДНД бот справочник. Помогу вам создать и запомню ваших персонажей!")


@dp.message(Command('create'))
async def address(message: types.Message):
    await message.reply("Пока пусто")


@dp.message(Command('check'))
async def phone(message: types.Message):
    await message.reply("Тут тоже пусто")


if __name__ == '__main__':
    asyncio.run(main())  # начинаем принимать сообщения