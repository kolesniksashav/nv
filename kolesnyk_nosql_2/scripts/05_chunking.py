import os
import re
import time
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import nltk

# Завантажуємо пунктуацію NLTK для правильного розбиття на речення
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
from nltk.tokenize import sent_tokenize

# 1. Ініціалізація та налаштування
load_dotenv()

INPUT_PARQUET = "data/arxiv_subset.parquet"
MODEL_NAME = "allenai/specter2_base"
INDEX_FIXED = "arxiv-chunks-fixed"
INDEX_SEMANTIC = "arxiv-chunks-semantic"

# Перевірка наявності API ключа
if "PINECONE_API_KEY" not in os.environ:
    raise ValueError("Помилка: PINECONE_API_KEY не знайдено в змінних оточення (.env файл).")

# Ініціалізація клієнта
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

print(f"Завантаження моделі {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

# Завантажуємо датасет та обираємо 30 найдовших абстрактів
df = pd.read_parquet(INPUT_PARQUET)
# Додаємо колонку з довжиною тексту в словах для точного відбору
df['abstract_word_count'] = df['abstract'].apply(lambda x: len(str(x).split()))
top_30_longest = df.nlargest(30, 'abstract_word_count').copy()

print(f"Обрано 30 статей із найдовшими анотаціями (довжина від {top_30_longest['abstract_word_count'].min()} до {top_30_longest['abstract_word_count'].max()} слів).")


# =====================================================================
# 2. Стратегії чанкінгу (Chunking Strategies)
# =====================================================================

# Стратегія А: Fixed-size chunking (Фіксований розмір слів із перекриттям)
def fixed_size_chunking(text, chunk_size=50, overlap=10):
    words = text.split()
    chunks = []
    if len(words) <= chunk_size:
        return [text]

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start += (chunk_size - overlap)
    return chunks

# Стратегія Б: Semantic chunking (Групування цілих речень)
def semantic_chunking(text, max_words=60):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        # Якщо одне речення саме по собі величезне, додаємо його як окремий чанк
        if sentence_word_count > max_words:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0
            chunks.append(sentence)
            continue

        if current_word_count + sentence_word_count > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_word_count = sentence_word_count
        else:
            current_chunk.append(sentence)
            current_word_count += sentence_word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# =====================================================================
# 3. Створення індексів у Pinecone
# =====================================================================
def prepare_pinecone_index(index_name):
    # Видаляємо старий індекс, якщо він існує, для чистоти експерименту
    if index_name in pc.list_indexes().names():
        print(f"Видалення старого індексу {index_name}...")
        pc.delete_index(index_name)
        time.sleep(2)

    print(f"Створення нового індексу {index_name}...")
    pc.create_index(
        name=index_name,
        dimension=768,  # Розмірність для specter2_base
        metric="dotproduct",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    # Очікуємо повної ініціалізації індексу серверами
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)
    return pc.Index(index_name)

idx_fixed = prepare_pinecone_index(INDEX_FIXED)
idx_semantic = prepare_pinecone_index(INDEX_SEMANTIC)


# =====================================================================
# 4 & 5. Обробка, генерація ембеддингів та завантаження батчами
# =====================================================================
# Додаємо аргумент index_name_str, щоб передавати туди назву індексу текстом
def process_and_upload_chunks(dataframe, chunk_function, pinecone_index, index_name_str, strategy_name):
    print(f"\nГенерація чанків та завантаження для стратегії: {strategy_name}...")
    vectors_to_upsert = []
    global_chunk_counter = 0

    for _, row in dataframe.iterrows():
        # Очищення тексту від зайвих переносів рядків
        clean_abstract = str(row['abstract']).replace('\n', ' ').strip()
        # Застосовуємо вибрану стратегію розбиття
        chunks = chunk_function(clean_abstract)

        for chunk_idx, chunk_text in enumerate(chunks):
            # Специфічний префікс моделі SPECTER2 для документів
            # (під час індексації документів інструкція зазвичай не потрібна, але ми використовуємо стандартний виклик)            
            embedding = model.encode(chunk_text, normalize_embeddings=True).tolist()
            # Унікальний ID чанка
            unique_id = f"chunk_{strategy_name}_{row['id']}_{chunk_idx}"
            # Формуємо об'єкт з метаданими
            meta = {
                "arxiv_id": str(row['id']),
                "title": str(row['title']),
                "text": chunk_text,
                "chunk_number": int(chunk_idx),
                "year": int(row['year']),
                "category": str(row['category'])
            }
            vectors_to_upsert.append((unique_id, embedding, meta))
            global_chunk_counter += 1

    # Завантаження в Pinecone батчами по 50 елементів з прогрес-баром
    batch_size = 50
    for i in tqdm(range(0, len(vectors_to_upsert), batch_size), desc=f"Завантаження в {index_name_str}"):
        batch = vectors_to_upsert[i:i + batch_size]
        pinecone_index.upsert(vectors=batch)

    print(f"Успішно завантажено {global_chunk_counter} чанків у {index_name_str}!")

# Запускаємо конвеєр для обох стратегій
process_and_upload_chunks(top_30_longest, lambda t: fixed_size_chunking(t, 50, 10), idx_fixed, INDEX_FIXED, "fixed")
process_and_upload_chunks(top_30_longest, lambda t: semantic_chunking(t, 60), idx_semantic, INDEX_SEMANTIC, "semantic")

# =====================================================================
# 6. Функція пошуку по чанках
# =====================================================================
def search_in_chunks(query_text, pinecone_index, title_label):
    print("\n" + "="*70)
    print(f" ПОШУК: {title_label} ")
    print("="*70)
    print(f"Запит: '{query_text}'")

    # Форматуємо запит із обов'язковим префіксом для моделі SPECTER2
    instruction = "Represent the Research Question for retrieving relevant documents: "
    query_vector = model.encode(instruction + query_text, normalize_embeddings=True).tolist()

    results = pinecone_index.query(vector=query_vector, top_k=5, include_metadata=True)

    for idx, match in enumerate(results.get("matches", [])):
        meta = match.get("metadata", {})
        print(f"\n{idx+1}. ID чанка: {match['id']} | Score: {match['score']:.4f}")
        print(f"   Назва статті: {meta.get('title')}")
        print(f"   Категорія: {meta.get('category')} | Номер чанка: {meta.get('chunk_number')}")
        # Виводимо частину (або весь) текст чанка
        print(f"   Текст чанка: {meta.get('text', '')[:180]}...")
        print("-" * 50)

# Тестові запити для перевірки пошуку по чанках
test_queries = [
    "mathematical models and algorithms",
    "experimental data analysis and simulation results"
]

# Очікуємо 5 секунд, щоб дані в Pinecone встигли повністю проіндексуватися перед пошуком
print("\nОчікування індексації даних на серверах Pinecone...")
time.sleep(5)

for query in test_queries:
    search_in_chunks(query, idx_fixed, "СТРАТЕГІЯ FIXED-SIZE CHUNKS")
    search_in_chunks(query, idx_semantic, "СТРАТЕГІЯ SEMANTIC CHUNKS")