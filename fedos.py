import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold

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

class Form(StatesGroup):
    name = State() 
    age = State() 
    gender = State()
    rase = State()
    img = State()
    inventory = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    content = Text("Привет, ", Bold(message.from_user.full_name))
    await message.answer(**content.as_kwargs())
    await message.answer(" Я ДНД бот! Давай создадим персонажа!\n"
                        "/create - создать нового персонажа\n"
                        "/check - просмотреть созданных персонажей\n"
                        "/help - справочник",reply_markup=kb)

@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока.", reply_markup=ReplyKeyboardRemove())


@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply("Я ДНД бот справочник. Помогу вам создать и запомню ваших персонажей!")


@dp.message(Command("create"))
async def address(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Как зовут вашего персонажа?")

@dp.message(Command("stop"))
@dp.message(F.text.casefold() == "stop")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return 

    logging.info("Остановились на шаге %r", current_state)
    await state.clear()
    await message.answer(
        "Всего доброго!",
    )

@dp.message(Form.name)
async def process_locality(message: types.Message, state: FSMContext):
    await state.set_state(Form.age)
    name = message.text
    await state.update_data(name=name) # сохраняем введенные данные во внутреннем хранилище
    await message.answer(
        f"Сколько лет {name}?")
    



@dp.message(Command('check'))
async def phone(message: types.Message):
    await message.reply("Тут тоже пусто")


if __name__ == '__main__':
    asyncio.run(main())  # начинаем принимать сообщения