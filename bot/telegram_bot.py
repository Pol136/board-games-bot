from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils import executor
import json
import csv
from datetime import datetime
import os
import aiohttp
import speech_recognition as sr
from pydub import AudioSegment

from config import API_TOKEN, ADMIN_ID
from main import bot, get_intent_ml

bot_instance = Bot(token=API_TOKEN)
dp = Dispatcher(bot_instance)


def get_order_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2)
    keyboard.add(
        types.KeyboardButton("Да, оформить заказ", web_app={'url': 'https://pol136.github.io/web_app_form/'}),
        types.KeyboardButton("Нет", callback_data='cancel_order')
    )
    return keyboard


# команда старт
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


# команда помощи
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


# команда для просмотра заказов
@dp.message_handler(commands=["orders"])
async def show_user_orders(message: types.Message):
    user_id = int(message.from_user.id)
    try:
        with open("orders.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = [row for row in reader if int(row[1]) == user_id]

        if not rows:
            await message.answer("У тебя пока нет заказов 😕")
            return

        response = "📦 Твои заказы:\n\n"
        for row in rows:
            order_id, user_id, username, name, pickup, games, status, timestamp = row

            response += (
                f"📦 Заказ №{order_id} от {timestamp}\n"
                f"Игры: {games}\n"
                f"Пункт выдачи: {pickup}\n"
                f"Статус: {status}\n\n"
            )

        await message.answer(response.strip())

    except FileNotFoundError:
        await message.answer("Список заказов пока пуст.")


# админская команда для изменения статуса заказа
@dp.message_handler(commands=["setstatus"])
async def set_status_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У тебя нет доступа к этой команде.")
        return

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❗ Используй формат: /setstatus <номер> <статус>")
        return

    order_id, new_status = args[1], args[2]
    updated = False
    rows = []

    try:
        with open("orders.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        for i in range(len(rows)):
            row = rows[i]
            if len(row) >= 8 and row[0].strip() == str(order_id).strip():
                # Обновляем статус
                row[6] = new_status
                updated = True

                # Получаем user_id и games
                user_id = int(row[1])
                games = row[5]

                # Сохраняем обратно
                rows[i] = row
                break

        if updated:
            with open("orders.csv", "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(rows)

            await message.answer(f"✅ Статус заказа №{order_id} обновлён на: {new_status}")

            # Уведомляем пользователя
            try:
                await bot_instance.send_message(
                    user_id,
                    f"📦 Статус твоего заказа №{order_id} обновлён:\n🎲 {games}\n🚚 Новый статус: {new_status}"
                )
            except Exception as e:
                print(e)
                await message.answer("⚠️ Не удалось отправить уведомление пользователю.")

        else:
            await message.answer("❌ Заказ с таким номером не найден.")

    except Exception as e:
        print("Ошибка при обновлении заказа:", e)
        await message.answer("⚠️ Не удалось обновить статус заказа.")


# Обработка обычных текстовых сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    print(">> Получено сообщение:", message.text)
    user_text = message.text
    intent = get_intent_ml(user_text)
    print(intent)

    if intent == "order_game":
        await message.answer(
            "Отличный выбор! Хочешь оформить заказ?",
            reply_markup=get_order_keyboard()
        )
        return

    # остальная логика
    response = bot(user_text)
    await message.answer(response)


@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    try:
        # Скачиваем файл
        file_id = message.voice.file_id
        file = await bot_instance.get_file(file_id)
        file_path = file.file_path
        voice_ogg = f"voice_{file_id}.ogg"
        voice_wav = f"voice_{file_id}.wav"

        await bot_instance.download_file(file_path, voice_ogg)

        # Конвертируем ogg → wav
        AudioSegment.from_file(voice_ogg).export(voice_wav, format="wav")

        # Распознаём речь
        recognizer = sr.Recognizer()
        with sr.AudioFile(voice_wav) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")

        # Удаляем временные файлы
        os.remove(voice_ogg)
        os.remove(voice_wav)

        # Ответ
        response = bot(text)
        await message.answer(f"Вы сказали: «{text}»\n\n📦 Ответ: {response}")

    except sr.UnknownValueError:
        await message.answer("😕 Я не смог разобрать, что вы сказали.")
    except Exception as e:
        print("❌ Ошибка при распознавании голоса:", e)
        await message.answer("⚠️ Не удалось обработать голосовое сообщение.")


# Обработчик нажатия кнопки Нет при предложении сделать заказ
@dp.callback_query_handler(lambda c: c.data == 'cancel_order')
async def cancel_order_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Хорошо! Если передумаешь — я здесь 🙂")


# обработчик данных с формы для создания заказа
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def process_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        name = data.get("name")
        pickup = data.get("pickup")
        games = data.get("games", [])

        if not name or not games:
            await message.answer("❗ Пожалуйста, укажи имя и выбери хотя бы одну игру.")
            return

        status = "в пути"
        user_id = str(message.from_user.id)
        username = message.from_user.username or "-"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Получаем номер нового заказа (индекс строки)
        try:
            with open("orders.csv", "r", encoding="utf-8") as f:
                order_id = sum(1 for _ in f)
        except FileNotFoundError:
            order_id = 1

        # Сохраняем заказ
        with open("orders.csv", "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                order_id,
                user_id,
                username,
                name,
                pickup,
                ", ".join(games),
                status,
                timestamp
            ])

        # Подтверждение пользователю
        text = f"✅ Заказ №{order_id} оформлен!\n\n" \
               f"👤 Имя: {name}\n" \
               f"📦 Пункт выдачи: {pickup}\n" \
               f"🎲 Игры:\n" + '\n'.join(f"— {g}" for g in games) + f"\n\n🚚 Статус: {status}"

        await message.answer(text)

    except Exception as e:
        print("[Ошибка WebApp]:", e)
        await message.answer("⚠️ Что-то пошло не так при оформлении заказа 😢")


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
