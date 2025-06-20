import re
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

# --- Очистка текста ---
def clean_and_lemmatize(text):
    text = text.lower()
    text = re.sub(r'[^а-яё0-9\s\-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    lemmas = [morph.parse(token)[0].normal_form for token in tokens]
    return ' '.join(lemmas)

def extract_keywords(text):
    # Очень простая эвристика: удаляем вопросительные слова
    blacklist = {'кто', 'что', 'где', 'когда', 'зачем', 'почему', 'как', 'сколько', 'такой', 'такая'}
    words = clean_and_lemmatize(text).split()
    keywords = [word for word in words if word not in blacklist]
    return ' '.join(keywords)