import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types, F

import sqlite3 # База данных
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # для музыки  magic



reply_keyboard = [[KeyboardButton(text='/create'), KeyboardButton(text='/help')],
                  [KeyboardButton(text='/check')],
                  [KeyboardButton(text='/magic')],
                  [KeyboardButton(text="/stop")]]

kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

dp = Dispatcher()
BOT_TOKEN = "7309765684:AAEYKRlw7HRhD7ypk3zwKzeSzQSHVcaPoKo"

async def main():
    bot = Bot(token=BOT_TOKEN)
    create_data_base()  
    await dp.start_polling(bot)

class Form(StatesGroup):
    name = State() 
    age = State() 
    gender = State()
    rase = State()
    img = State()
    inventory = State()

# Если пользователь есть он приветствует если нет, то нет
def create_data_base(): # Cоздаем базу данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def check_person(user_id): # Проверяем, что пользователь есть в базе данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone() # не пон
    conn.close()
    return user is None # Никого нет найн

def dobavka_person(user_id): # Добавляем его если его нет
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if check_person(user_id):
        dobavka_person(user_id)
        await message.answer(f"Привет, {first_name}! Вижу ты у нас впервые! Познакомимся?\n"
                            "Я ДНД бот. Давай создадим персонажа!\n"
                            "/create - создать нового персонажа\n"
                            "/check - просмотреть созданных персонажей\n"
                            "/help - справочник", reply_markup=kb)
    else:
        await message.answer(f"С возвращением, {first_name}! Рад тебя снова видеть! \n"
                            "/create - создать нового персонажа\n"
                            "/check - просмотреть созданных персонажей\n"
                            "/help - справочник", reply_markup=kb)



# НЕ РАБООТАЕТ
#@dp.message(Command("stop"))
#@dp.message(F.text.casefold() == "stop")
#async def cancel_handler(message: types.Message, state: FSMContext):
#    current_state = await state.get_state()
#    if current_state is None:
#        return 
#
#    logging.info("Остановились на шаге %r", current_state)
#    await state.clear()
#    await message.answer(
#        "Всего доброго!",
#    )
# НЕ РАБООТАЕТ


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока.", reply_markup=ReplyKeyboardRemove())



@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply("Я ДНД бот справочник. Помогу создать и запомню ваших персонажей!")

@dp.message(Command("create"))
async def address(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Как зовут вашего персонажа?")

@dp.message(Command('check'))
async def phone(message: types.Message):
    await message.reply("Тут тоже пусто")

@dp.message(Command("magic"))
async def magic_button(message: types.Message):
    keyboard = InlineKeyboardButton(text='Сообщение 2', callback_data='message_2')
    await message.answer(keyboard)

    
@dp.message(Form.name)
async def process_locality(message: types.Message, state: FSMContext):
    name = message.text
    await state.set_state(Form.age)
    await state.update_data(name=name) # сохраняем введенные данные во внутреннем хранилище
    await message.answer(f"Введите возраст персонажа {name}")


################################################
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    await state.set_state(Form.gender)
    await state.update_data(age=age) # сохраняем введенные данные во внутреннем хранилище
    await message.answer("Введите пол персонажа")


@dp.message(Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text
    await state.set_state(Form.rase)
    await state.update_data(gender=gender) # сохраняем введенные данные во внутреннем хранилище
    await message.answer("Введите расу персонажа")

@dp.message(Form.rase)
async def process_rase(message: types.Message, state: FSMContext):
    rase = message.text
    await state.set_state(Form.inventory)
    await state.update_data(rase=rase) # сохраняем введенные данные во внутреннем хранилище
    await message.answer("Введите какой инвентарь будет у персонажа")

@dp.message(Form.inventory)
async def process_inventory(message: types.Message, state: FSMContext):
    inventory = message.text
    await state.update_data(inventory=inventory)

    data = await state.get_data()
    inventory = (
        f"Имя: {data['name']}\n"
        f"Возраст: {data['age']}\n"
        f"Пол: {data['gender']}\n"
        f"Раса: {data['rase']}\n"
        f"Инвентарь: {data['inventory']}\n"
    )
    with sqlite3.connect('list.db') as cnn:
        cnn.execute(
            """
        create table if not exists data
        (
            id     INTEGER
                primary key autoincrement,
            name   TEXT,
            age    INT,
            gender TEXT,
            rase   TEXT,
            inventory TEXT
        );
        """)

        cnn.execute(
            """

            create unique index if not exists data_name_uindex
                on data (name);

                """
        )
        cr = cnn.cursor()
        try:
            cr.execute(
                """
                INSERT INTO data (name, age, gender, rase, inventory)
                            VALUES (:name, :age, :gender, :rase, :inventory)
                    on conflict (name) do
                    update
                        set age = excluded.age
                """,
                data
            )
        except Exception:
            cnn.rollback()
            cr.close()
            raise
        else:
            cnn.commit()
            cr.close()
    await state.update_data(inventory=inventory) # сохраняем введенные данные во внутреннем хранилище
    await message.answer(f"Ваш персонаж создан:\n\n{inventory}")
    await state.clear()
################################################

if __name__ == '__main__':
    asyncio.run(main())
