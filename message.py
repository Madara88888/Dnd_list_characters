import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, types, F

import sqlite3 # База данных
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup # для музыки  magic


import random # Кубики
import requests

reply_keyboard = [[KeyboardButton(text='/create'), KeyboardButton(text='/check')],
                  [KeyboardButton(text='/help')],
                  [KeyboardButton(text='/magic'), KeyboardButton(text='/dict')],
                  [KeyboardButton(text='/monster_manual'), KeyboardButton(text='/dice')],
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

class Dice(StatesGroup):
    name_dice = State()
    count_dice = State()

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


@dp.message(Command("dict"))
async def dictionary_intro(message: types.Message, state: FSMContext):
    await message.answer("Привет, ты можешь написать любое слово, а я расскажу определение этого слова.")
    await state.set_state("waiting_for_word")  # ждем сообщения


@dp.message(StateFilter("waiting_for_word")) # Обработка введенного слова и поиск определения
async def define_word(message: types.Message, state: FSMContext):
    word = message.text

    if wikipedia_api(word):
        await message.answer(wikipedia_api(word))
    else:
        await message.answer(f"Попробуйте другое слово. Напишите /dict снова")

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
async def show_dice_options(message: types.Message, state: FSMContext):
    await state.set_state(Dice.name_dice)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Бросить кубик d4"), KeyboardButton(text="Бросить кубик d6")],
            [KeyboardButton(text="Бросить кубик d8"), KeyboardButton(text="Бросить кубик d12")],
            [KeyboardButton(text="Бросить кубик d16"), KeyboardButton(text="Бросить кубик d20")],
            [KeyboardButton(text="Бросить кубик d100"), KeyboardButton(text="Стоп")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите тип кубика:", reply_markup=keyboard)


@dp.message(Dice.name_dice)
async def count_dice(message: types.Message, state: FSMContext):
    name_dice = message.text
    type_dice = name_dice.split("d")
    if "кубик d" in name_dice:
        try:
            await state.set_state(Dice.count_dice)
            await state.update_data(name=int(type_dice[-1]))
            await message.answer(f" Сколько кубиков вы хотите бросить?")
        except ValueError:
            await message.answer("d(тут не целое число)") 
    elif "Стоп" in name_dice: # Сделать кнопку пока на выход 
        await message.answer("Хорошо!", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Я не знаю такой тип кубика. напишите: кубик d(число)")


@dp.message(Dice.count_dice)
async def handle_dice_message(message: types.Message, state: FSMContext):
    count_dice = message.text
    await state.update_data(count=count_dice)
    data = await state.get_data()
    try:
        for i in range(int(data['count'])):
            x = random.randint(1, int(data['name']))
            await message.answer(f"Выпало: {x}")
        await message.answer(f"готово!", reply_markup=kb)
    except ValueError:
        await message.answer("Не целое число!")
    
    await state.clear()


@dp.message(Command('stop'))
async def stop(message: types.Message):
    await message.reply("Пока.", reply_markup=ReplyKeyboardRemove())


@dp.message(Command('help'))
async def help(message: types.Message):
    await message.reply("Я ДНД бот справочник. Помогу создать и запомню ваших персонажей!")
    await message.answer(f"Мои функции: \n"
                            "  /create - создать нового персонажа\n"
                            "  /check - просмотреть созданных персонажей\n"
                            "  /magic - показывает ВАЖНОЕ видео\n"
                            "  /monster_manual - показывает случайного монстра\n"
                            "  /dice - позволяет бросать кубики\n"
                            "  /dict - Расказывает вам о любом слове\n",
                              reply_markup=kb)

@dp.message(Command("create"))
async def address(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Как зовут вашего персонажа?")

@dp.message(Command('check'))
async def phone(message: types.Message):
    con = sqlite3.connect('list.db')
    cur = con.cursor()
    res = cur.execute("SELECT * FROM data")
    num_hero = 1
    for k in res.fetchall():
        text = as_list(
            as_marked_section(
            Bold(f"№:{num_hero}"),
            f"Имя: {k[2]}",
            f"Возраст: {k[3]}",
            f"Пол: {k[4]}",
            f"Раса: {k[5]}",
            f"Инвентарь: {k[6]}",
            marker="✨  "))
        if k[1] == message.from_user.id:
            num_hero += 1
            if k[7] != None:
                await message.answer_photo(photo=k[7], caption="⏬⏬⏬")
                await message.answer(**text.as_kwargs())
            else:
                await message.answer(**text.as_kwargs())     


@dp.message(Command("magic"))
async def magic_button(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Нажми меня", url="https://www.youtube.com/watch?v=y75VErslEVQ")]
        ]
    )
    await message.answer("Нажми ее:", reply_markup=keyboard)

@dp.message(Command("monster_manual"))
async def magic_button(message: types.Message):
    url = "https://www.dnd5eapi.co/api/2014/monsters/"
    payload = {}
    headers = {
    'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    d = []
    for i in response.text[24:-2].split('{'):
        i = i.split(',')
        i = i[1:]
        if i == []:
            continue
        if i[-1] == '':
            i = i[:-1]
        s = []
        if len(i) == 3:
            s.append(f'{i[0][8:]}:{i[1][:-1]}')
            s.append(i[2][16:-2])
        else:
            s.append(i[0][8:-1])
            s.append(i[1][16:-2])
        d.append(s)
    
    r = random.randint(0, (len(d) -1))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{d[r][0]}!", url=f"https://www.dndbeyond.com/{d[r][1]}")]
        ]
    )
    await message.answer(f"Ваш монстр - это:", reply_markup=keyboard)

    
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
    data["user_id"] = message.from_user.id # добавляем айдишники в таблицу
    
    text = (
        f"Имя: {data['name']} \n"
        f"Возраст: {data['age']} \n"
        f"Пол: {data['gender']} \n"
        f"Раса: {data['rase']} \n"
        f"Инвентарь: {data['inventory']}"
    )

    with sqlite3.connect('list.db') as list: # NEWWWW ДОБАВИЛ img TEXT!!!!!!!!!!
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
                    img TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                """
        )
        cursor_list = list.cursor()
        try: # NEWWWW ДОБАВИЛ img TEXT!!!!!!!!!!
            cursor_list.execute(
                """
                INSERT INTO data (name, user_id, age, gender, rase, img, inventory)
                VALUES (:name, :user_id, :age, :gender, :rase, :img, :inventory)
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