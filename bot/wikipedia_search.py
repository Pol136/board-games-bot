import wikipedia
from text_utils import extract_keywords
import re

wikipedia.set_lang("ru")

MANUAL_TOPICS = {
    'имаджинариум': 'Имаджинариум (настольная игра)',
    'каркассон': 'Каркассон (настольная игра)',
    '7 чудес': '7 чудес (настольная игра)',
    'настольные игры': 'Настольная игра'
}


def getwiki(query):
    try:
        page = wikipedia.page(query)
        wikitext = page.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = [x for x in wikimas if '==' not in x and len(x.strip()) > 3]
        text = '.'.join(wikimas)
        text = re.sub('\([^()]*\)', '', text)
        text = re.sub('\{[^\{\}]*\}', '', text)
        return text.strip()
    except Exception:
        return 'В энциклопедии нет информации об этом'


def search_in_wikipedia(text):
    query = extract_keywords(text).lower()

    for key in MANUAL_TOPICS:
        if key in query:
            return getwiki(MANUAL_TOPICS[key])

    # fallback: обычный поиск
    results = wikipedia.search(query)
    if results:
        return getwiki(results[0])

    return None


def wants_wikipedia(text):
    return 'вики' in text.lower() or 'wiki' in text.lower()

