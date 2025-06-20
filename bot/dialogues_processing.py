import json

alphabet = ' абвгдеёжзийклмнопрстуфхцчшщъыьэюя-1234567890'

def clean_text(text):
    return ''.join(ch for ch in text.lower().strip() if ch in alphabet)

# 1. Чтение исходного диалога
with open("dialogues.txt", encoding="utf-8") as f:
    content = f.read()

blocks = content.split('\n\n')
dataset = []

# 2. Очистка и сбор пар
for block in blocks:
    replicas = block.strip().split('\n')[:2]
    if len(replicas) == 2:
        question = clean_text(replicas[0][2:])  # удаляем тире и пробел в начале
        answer = clean_text(replicas[1][2:])
        if question and answer:
            dataset.append((question, answer))

print(f"Собрано {len(dataset)} пар вопрос–ответ")

# 3. Сохраняем в JSON
with open("cleaned_dialogues.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)
