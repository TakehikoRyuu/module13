# Машина состояний \ Клавиатура кнопок \ Инлайн клавиатуры
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = '8189490910:AAH8omJrs3Uiiw3ldv2sHpRavqY3sopq55I'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.row(button1, button2)

kb_calories = InlineKeyboardMarkup()
but_calo_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
but_calo_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_calories.add(but_calo_1)
kb_calories.add(but_calo_2)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb_calories)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(f'10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (г) - 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Для подсчёта калорий необходимы некоторые данные. ' 
                         'Пожалуйста, пишите все значения без букв и аббревиатур.')
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    await message.answer('Введите свой рост:')
    await UserState.growth.set()




@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес:')
    await UserState.weight.set()



@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    try:
        await state.update_data(weight=message.text)
        data = await state.get_data()
        weight = float(data['weight'])
        growth = float(data['growth'])
        age = int(data['age'])
        calories = 10 * weight + 6.25 * growth - 5 * age - 161
        await message.answer(f"Ваша норма калорий - {calories}")
    except ValueError:
        await message.answer("Ошибка: все значения должны быть числовыми.")
        await state.finish()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb)


@dp.message_handler()
async def all_massages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)