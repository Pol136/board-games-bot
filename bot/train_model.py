# train_model.py
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from bot_config import BOT_CONFIG
import pymorphy2
import re

# Инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer()

# Функция для очистки и лемматизации текста
def clean_and_lemmatize(text):
    text = text.lower()
    text = re.sub(r'[^а-яё0-9\s\-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    return ' '.join(lemmas)

# Подготовка обучающей выборки
X_text = []
y = []

for intent, intent_data in BOT_CONFIG['intents'].items():
    for example in intent_data['examples']:
        lemmatized = clean_and_lemmatize(example)
        X_text.append(lemmatized)
        y.append(intent)

# Векторизация слов (анализ по словам!)
vectorizer = TfidfVectorizer(analyzer='word')
X = vectorizer.fit_transform(X_text)

# Обучение модели
clf = LinearSVC()
clf.fit(X, y)

# Сохраняем модель и векторизатор
with open('intent_model.pkl', 'wb') as f:
    pickle.dump(clf, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ Модель обучена на леммах и сохранена.")
