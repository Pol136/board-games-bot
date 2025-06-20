# train_model.py
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from bot_config import BOT_CONFIG

# Подготовка данных
X_text = []
y = []

for intent, intent_data in BOT_CONFIG['intents'].items():
    for example in intent_data['examples']:
        X_text.append(example)
        y.append(intent)

# Обучение
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
X = vectorizer.fit_transform(X_text)
clf = LinearSVC()
clf.fit(X, y)

# Сохранение модели и векторизатора
with open('intent_model.pkl', 'wb') as f:
    pickle.dump(clf, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ Модель обучена и сохранена.")
