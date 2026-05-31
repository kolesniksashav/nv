import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# 1. Ініціалізація та налаштування
# Автоматично зчитуємо файл .env, де зберігається PINECONE_API_KEY
load_dotenv()

INPUT_PARQUET = "data/arxiv_subset.parquet"
INDEX_NAME = "arxiv-papers"
MODEL_NAME = "allenai/specter2_base"

# Перевірка наявності API ключа
if "PINECONE_API_KEY" not in os.environ:
    raise ValueError("Помилка: PINECONE_API_KEY не знайдено в змінних оточення (.env файл).")

# Підключення до Pinecone та завантаження моделі
# Ініціалізуємо базовий клієнт Pinecone, передаючи секретний API-ключ
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
# Підключаємося до вже створеного раніше індексу ("arxiv-papers")
index = pc.Index(INDEX_NAME)
# Завантажуємо модель через бібліотеку sentence-transformers
print(f"Завантаження моделі {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

# Завантаження датасету
print(f"Завантаження корпусу статей з {INPUT_PARQUET}...")
df = pd.read_parquet(INPUT_PARQUET)
df['id'] = df['id'].astype(str)

# Об'єднуємо заголовок та анотацію для повноцінного текстового індексу BM25
df['full_text'] = df['title'] + " " + df['abstract']

# =====================================================================
# 2. Побудова локального індексу BM25
# =====================================================================
print("Побудова локального індексу BM25...")
# Токенізація: переводимо в нижній регістр і ділимо на слова (базова очистка)
tokenized_corpus = [str(text).lower().split() for text in df['full_text'].values]
bm25 = BM25Okapi(tokenized_corpus)


# =====================================================================
# 3. Реалізація функцій пошуку (BM25, Векторний, Гібридний)
# =====================================================================

# А. Локальний пошук BM25
def search_bm25(query_text, top_k=10):
    # Крок 1: Приведення до нижнього регістру та розбиття запиту на окремі слова-токени
    tokenized_query = query_text.lower().split()    
    # Крок 2: Розрахунок лексичних скорів для всіх 10,000 статей корпусу
    scores = bm25.get_scores(tokenized_query)
    # Крок 3: Сортування масиву скорів за спаданням та відбір індексів найкращих статей
    top_indices = np.argsort(scores)[::-1][:top_k]
    # Крок 4: Формування стандартизованого списку результатів
    results = []
    for rank, idx in enumerate(top_indices):
        if scores[idx] == 0:  # Пропускаємо статті без збігів
            continue
        results.append({
            "id": f"paper_{df.iloc[idx]['id']}",
            "title": df.iloc[idx]['title'],
            "rank": rank + 1,
            "score": float(scores[idx]),
            "method": "BM25"
        })
    return results

# Б. Векторний пошук у Pinecone
def search_vector(query_text, top_k=10):
    # Крок 1: Обов'язкова інструкція-префікс, яку вимагає архітектура SPECTER2 для пошукових запитів
    instruction = "Represent the Research Question for retrieving relevant documents: "
    # Крок 2: Склеюємо інструкцію із запитом та генеруємо вектор (ембеддинг)
    # Параметр normalize_embeddings=True приводить довжину вектора до 1.0 (L2-нормалізація)
    query_vector = model.encode(instruction + query_text, normalize_embeddings=True).tolist()
    
    # Крок 3: Робимо безпосередній векторний пошук у хмарі Pinecone
    response = index.query(
        vector=query_vector,       # Передаємо згенерований 768-вимірний список чисел
        top_k=top_k,               # Вказуємо, скільки найближчих сусідів (статей) повернути
        include_metadata=True      # Просимо повернути метадані (title, abstract, year тощо)
    )
    # Крок 4: Форматуємо відповідь від Pinecone у зручний список словників
    results = []
    for rank, match in enumerate(response.get("matches", [])):
        metadata = match.get("metadata", {})
        results.append({
            "id": match['id'],
            "title": metadata.get("title", ""),
            "rank": rank + 1,
            "score": float(match['score']), # Скор близькості (в нашому випадку Dot Product)
            "method": "Vector"
        })
    return results

# В. Гібридний пошук через Reciprocal Rank Fusion (RRF)
def search_hybrid(query_text, top_k=5, k_rrf=60):
    # Беремо з кожного методу трохи більше результатів (наприклад, 20), щоб було що об'єднувати
    # Крок 1: Отримуємо розширені списки кандидатів (по 20 штук) від кожного методу.
    # Це необхідно, щоб знайти перетини — документи, які один метод поставив на 2-ге місце, а інший — на 15-те.    
    bm25_res = search_bm25(query_text, top_k=20)
    vector_res = search_vector(query_text, top_k=20)
    # Словники для накопичення фінальних RRF-балів та збереження назв статей
    rrf_scores = {}
    doc_titles = {}
    
    # Крок 2: Обробка списку BM25
    for doc in bm25_res:
        doc_id = doc['id']
        doc_titles[doc_id] = doc['title']
        # Додаємо до рейтингу документа значення: 1 / (60 + місце_в_БМ25)
        # Формула RRF: 1 / (k + rank)
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_rrf + doc['rank']))
        
    # Крок 3: Обробка результатів векторного пошуку
    for doc in vector_res:
        doc_id = doc['id']
        doc_titles[doc_id] = doc['title']
        # Якщо документ вже був знайдений через BM25, його ранг сумується!
        # Додаємо значення: 1 / (60 + місце_в_Векторі)        
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (k_rrf + doc['rank']))
        
    # Крок 4: Сортування та формування загального Топ-K
    # Сортування документів за фінальним RRF-скором
    # Сортуємо словник за значенням скору (x[1]) у зворотному порядку (reverse=True)    
    sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    # Крок 5: Пакуємо фінальний результат у красивий формат
    hybrid_results = []
    for rank, (doc_id, score) in enumerate(sorted_docs):
        hybrid_results.append({
            "id": doc_id,
            "title": doc_titles[doc_id],
            "rank": rank + 1,
            "score": score,
            "method": "Hybrid_RRF"
        })
    return bm25_res[:top_k], vector_res[:top_k], hybrid_results


# =====================================================================
# 4. Демонстрація та запуск тестових запитів
# =====================================================================
# Визначаємо три контрастні типи запитів відповідно до ТЗ
test_queries = {
    "Точний термін": "BERT fine-tuning",
    "Ім’я автора": "Yann LeCun convolutional networks",
    "Перефразування": "making computers understand human emotions from text"
}
# Запуск циклу для демонстрації
for query_type, text in test_queries.items():
    print("\n" + "="*80)
    print(f" ЗАПИТ ({query_type}): '{text}' ")
    print("="*80)
    # Викликаємо гібридний пошук. Він повертає нам зрізи Top-5
    # для кожного з трьох методів окремо.    
    bm25_top5, vector_top5, hybrid_top5 = search_hybrid(text, top_k=5)
    
    # -----------------------------------------------------------------
    # БЛОК 1: Виведення результатів для чисого BM25 (Лексичний пошук)
    # -----------------------------------------------------------------
    print(f"\n[ Top-5 BM25 ]")
    if not bm25_top5:
        # Важливо для третього запиту (перефразування): 
        # якщо точних слів немає в базі, виводимо зрозуміле попередження        
        print("  Нічого не знайдено за точними термінами.")
    for doc in bm25_top5:
        # Виводимо ранг, ID, сирий скор BM25 та перші 75 символів назви статті
        print(f"  {doc['rank']}. ID: {doc['id']} | Score: {doc['score']:.2f} | {doc['title'][:75]}...")
        
    # -----------------------------------------------------------------
    # БЛОК 2: Виведення результатів для чистого Векторного пошуку
    # -----------------------------------------------------------------
    print(f"\n[ Top-5 ВЕКТОРНИЙ ПОШУК ]")
    for doc in vector_top5:
        # Виводимо ранг, ID, косинусний скор Pinecone та назву статті
        print(f"  {doc['rank']}. ID: {doc['id']} | Score: {doc['score']:.4f} | {doc['title'][:75]}...")
        
    # -----------------------------------------------------------------
    # БЛОК 3: Виведення результатів для фінального Гібридного пошуку з RRF
    # -----------------------------------------------------------------
    print(f"\n[ Top-5 ГІБРИДНИЙ ПОШУК (RRF) ]")
    for doc in hybrid_top5:
        # Виводимо фінальний RRF-скор, ID та назву статті
        # Саме тут ми бачимо синергію об'єднання двох методів        
        print(f"  {doc['rank']}. RRF Score: {doc['score']:.5f} | ID: {doc['id']} | {doc['title'][:75]}...")