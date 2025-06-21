import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from bot_config import BOT_CONFIG
import pymorphy2
import re
from sklearn.svm import LinearSVC
from text_utils import clean_and_lemmatize

# Инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer()

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

print("Модель обучена и сохранена")
