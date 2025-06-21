from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.utils import executor

from config import API_TOKEN
from main import bot, get_intent_ml
# from bot_logic import bot

# Создаём бота и диспетчер
bot_instance = Bot(token=API_TOKEN)
dp = Dispatcher(bot_instance)

def get_order_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Да, оформить заказ", web_app={'url': 'https://example.com/order-form'}),
        InlineKeyboardButton("Нет", callback_data='cancel_order')
    )
    return keyboard


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
@dp.message_handler()
async def handle_message(message: types.Message):
    user_text = message.text
    intent = get_intent_ml(user_text)

    if intent == "order_game":
        await message.answer(
            "Отличный выбор! Хочешь оформить заказ?",
            reply_markup=get_order_keyboard()
        )
        return

    # остальная логика
    response = bot(user_text)
    await message.answer(response)


# Обработчик нажатия кнопки Нет при предложении сделать заказ
@dp.callback_query_handler(lambda c: c.data == 'cancel_order')
async def cancel_order_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Хорошо! Если передумаешь — я здесь 🙂")



# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
