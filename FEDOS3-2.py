import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types, F

import sqlite3 # База данных
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup # для музыки  magic


import random # Кубики
import requests

from aiogram.filters import StateFilter

reply_keyboard = [[KeyboardButton(text='/create'), KeyboardButton(text='/help')],
                  [KeyboardButton(text='/check')],
                  [KeyboardButton(text='/magic')],
                  [KeyboardButton(text='/dice')],
                  [KeyboardButton(text='/slovar')],
                  [KeyboardButton(text="/stop")]
                  ]

kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
user_true_id = 1
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
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user INT
        )
    """)
    conn.commit()
    conn.close()

def check_person(user_id): # Проверяем, что пользователь есть в базе данных
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user = ?", (user_id,))
    user = cursor.fetchone()
    user_true_id = user
    conn.close()
    return user is None, user_true_id # Никого нет найн

def dobavka_person(user_id): # Добавляем его если его нет
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    if check_person(user_id)[0]:
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

################################################# API



@dp.message(Command("slovar"))
async def dictionary_intro(message: types.Message, state: FSMContext):
    await message.answer("Привет, ты можешь написать любое слово, а я расскажу определение этого слова.")
    await state.set_state("waiting_for_word")  # ждем сообщения


@dp.message(StateFilter("waiting_for_word")) # Обработка введенного слова и поиск определения
async def define_word(message: types.Message, state: FSMContext):
    word = message.text

    if wikipedia_api(word):
        await message.answer(wikipedia_api(word))
    else:
        await message.answer(f"Попробуйте другое слово. Напишите /slovar снова")

    await state.clear() # приходится всегда писать команду


def wikipedia_api(term: str, lang: str = "ru"):
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{term}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "extract" in data:
            return data["extract"]
    return None

################################################# API



@dp.message(Command('dice')) # Бросание кубиков
async def show_dice_options(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Бросить обычный кубик")],
            [KeyboardButton(text="Бросить 2 кубика")],
            [KeyboardButton(text="Бросить один с 20-ю гранями")],
            [KeyboardButton(text="Стоп")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите тип кубика:", reply_markup=keyboard)


@dp.message(F.text.lower().startswith("бросить")) # Ответ на броски
async def handle_dice_message(message: types.Message):
    text = message.text.lower()
    if "2 кубика" in text:
        result1 = random.randint(1, 6)
        result2 = random.randint(1, 6)
        await message.answer(f" Выпало: {result1} и {result2}")
    elif "обычный" in text:
        result = random.randint(1, 6)
        await message.answer(f" Выпало: {result}")
    elif "20" in text:
        result = random.randint(1, 20)
        await message.answer(f"Выпало: {result}")
    elif "Стоп" in text: # Сделать кнопку пока на выход 
        pass
    else:
        await message.answer("Я не знаю такой тип кубика. Попробуйте d6, 2d6 или d20.")


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
    con = sqlite3.connect('list.db')
    cur = con.cursor()
    res = cur.execute("SELECT * FROM data")
    await message.answer(f'{res.fetchall()}')   


@dp.message(Command("magic"))
async def magic_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Нажми меня", url="https://www.youtube.com/watch?v=y75VErslEVQ")]
        ]
    )
    await message.answer("Нажми ее:", reply_markup=keyboard)

    
@dp.message(Form.name)
async def process_locality(message: types.Message, state: FSMContext):
    name = message.text
    await state.set_state(Form.age)
    await state.update_data(name=name) # сохраняем введенные данные во внутреннем хранилище
    await message.answer(f"Введите возраст персонажа {name}")


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



############################# ФОТО ПЕРСОНАЖА
@dp.message(Form.rase)
async def process_rase_and_image(message: types.Message, state: FSMContext):
    rase = message.text
    await state.update_data(rase=rase)
    await state.set_state(Form.img)
    await message.answer("Теперь давай загрузим фото твоего персонажа! Если не хочешь — напиши 'Нет'")

@dp.message(Form.img, F.photo) # Если отправил фотку
async def take_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(img=photo_id)
    await state.set_state(Form.inventory)
    await message.answer("Теперь напиши инвентарь персонажа:")
    

@dp.message(Form.img) # Если пользователь сказал нет
async def skip_photo(message: types.Message, state: FSMContext):
    if message.text.strip().lower() == "нет":
        await state.update_data(img=None)
        await state.set_state(Form.inventory)
        await message.answer("Хорошо, без изображения. Теперь напиши инвентарь персонажа:")
    else:
        await message.answer("Пожалуйста, отправь фото или напиши 'Нет', если не хочешь добавлять изображение.")
#############################



@dp.message(Form.inventory)
async def process_inventory(message: types.Message, state: FSMContext):
    inventory = message.text
    await state.update_data(inventory=inventory)
    
    data = await state.get_data()
    
    text = (
        f"Имя: {data['name']} \n"
        f"Возраст: {data['age']} \n"
        f"Пол: {data['gender']} \n"
        f"Раса: {data['rase']} \n"
        f"Инвентарь: {data['inventory']}"
    )

    with sqlite3.connect('list.db') as list:
        list.execute(
            """
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                name TEXT,
                age INT,
                gender TEXT,
                rase TEXT,
                inventory TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            """
        )
        cursor_list = list.cursor()
        try:
            # cursor_list.execute("INSERT INTO data (user_id) VALUES (?)", check_person(message.from_user.id)[1])
            cursor_list.execute(
                """
                INSERT INTO data (name, age, gender, rase, inventory)
                VALUES (:name, :age, :gender, :rase, :inventory)
                """,
                data
            )
        except Exception:
            list.rollback()
            cursor_list.close()
            raise
        else:
            list.commit()
            cursor_list.close()

    await state.clear()

    
    if data.get("img"): # Если фото пользователь отправил - мы кидаем его если нет, то кидаем без него
        await message.answer_photo(photo=data["img"], caption=text)
    else:
        await message.answer(f"Ваш персонаж создан:\n\n{text}")

if __name__ == '__main__':
    asyncio.run(main())