from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.utils import executor

from config import API_TOKEN
from main import bot
# from bot_logic import bot

# Создаём бота и диспетчер
bot_instance = Bot(token=API_TOKEN)
dp = Dispatcher(bot_instance)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот, который поможет тебе подобрать настольную игру 🎲\n\n"
        "Я умею:\n"
        "— рекомендовать игры по жанру\n"
        "— рассказывать про стоимость\n"
        "— оформлять заказ\n"
        "— искать факты в Википедии (напиши `вики Каркассон`)\n\n"
        "Попробуй задать мне вопрос, например:\n"
        "🗣 «Посоветуй игру для вечеринки»"
    )


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await message.answer(
        "📚 Я могу:\n"
        "— Предложить настольные игры\n"
        "— Рассказать про Имаджинариум, Каркассон, 7 чудес и другие\n"
        "— Найти информацию в Википедии (если ты напишешь `вики <тема>`)\n\n"
        "Примеры запросов:\n"
        "🗨 «Помоги с выбором настольной игры»\n"
        "🗨 «Семейная игра»\n"
        "🗨 «вики Имаджинариум»\n\n"
        "Если не знаешь, что спросить — просто начни диалог 🙂"
    )


# Обработка обычных текстовых сообщений
@dp.message_handler(content_types=['text'])
async def handle_message(message: Message):
    user_text = message.text
    reply = bot(user_text)
    await message.answer(reply)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
