import random
import pickle
import json
import nltk
import warnings

from text_utils import clean_and_lemmatize
from bot_config import BOT_CONFIG
from wikipedia_search import search_in_wikipedia, wants_wikipedia

warnings.filterwarnings("ignore", category=UserWarning)


nltk.download('punkt')


# --- Загрузка модели ---
with open('intent_model.pkl', 'rb') as f:
    clf = pickle.load(f)

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# --- Загрузка диалогов ---
with open('cleaned_dialogues.json', encoding='utf-8') as f:
    dataset = json.load(f)
    # dataset = random.sample(dataset, 1000)

# def clean_text(text):
#     alphabet = ' абвгдеёжзийклмнопрстуфхцчшщъыьэюя-1234567890'
#     return ''.join(ch for ch in text.lower() if ch in alphabet)

# --- Генерация ответа из диалогов ---
def get_generative_answer(text):
    text = clean_and_lemmatize(text)
    candidates = []

    for question, answer in dataset:
        if abs(len(text) - len(question)) / len(question) < 0.2:
            dist = nltk.edit_distance(text, question)
            if dist / len(question) < 0.3:
                candidates.append((dist, answer))

    if candidates:
        return min(candidates, key=lambda x: x[0])[1]

# --- ML-предсказание намерения ---
def get_intent_ml(text):
    lemmatized = clean_and_lemmatize(text)
    text_vector = vectorizer.transform([lemmatized])
    return clf.predict(text_vector)[0]

# --- Ответ по намерению ---
def get_answer_by_intent(intent):
    return random.choice(BOT_CONFIG['intents'][intent]['responses'])

# --- Фраза по умолчанию ---
def get_failure_phrase():
    return random.choice(BOT_CONFIG['failure_phrases'])

# --- Главная функция бота ---
def bot(text):
    try:
        # 1. Если явно просит Википедию
        if wants_wikipedia(text):
            wiki = search_in_wikipedia(text)
            if wiki:
                return wiki
            return "Я не нашёл подходящую статью в Википедии 😕"

        # 2. Классификация намерения
        intent = get_intent_ml(text)
        if intent:
            return get_answer_by_intent(intent)

        # 3. Генеративный ответ
        answer = get_generative_answer(text)
        if answer:
            return answer

        return get_failure_phrase()
    except Exception as e:
        print("Ошибка:", e)
        return "Что-то пошло не так..."


# --- Консольное тестирование ---
if __name__ == '__main__':
    print("🎲 ГеймБот готов к работе. Пиши что-нибудь:")
    while True:
        msg = input("> ")
        if msg.lower() in ['выход', 'exit', 'quit']:
            print("Бот: До встречи!")
            break
        print("Бот:", bot(msg))
