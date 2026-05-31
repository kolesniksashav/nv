import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# 1. Підключення та завантаження
load_dotenv()

INPUT_PARQUET = "data/arxiv_subset.parquet"
INPUT_EMBEDDINGS = "embeddings/embeddings.npy"
INDEX_NAME = "arxiv-papers"
MODEL_NAME = "allenai/specter2_base"

# Перевірка наявності API ключа
if "PINECONE_API_KEY" not in os.environ:
    raise ValueError("Помилка: PINECONE_API_KEY не знайдено в змінних оточення (.env файл).")

# Ініціалізація клієнта
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(INDEX_NAME)

print(f"Завантаження моделі {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)

# 2. Функція кодування запиту в ембеддинг (із правильним префіксом для SPECTER2)
def get_query_embedding(query_text):
    # Для моделей серії SPECTER 2 обов'язково додавати цей префікс до пошукового запиту!
    # Це змушує модель працювати в режимі "запит до статті"  
    instruction = "Represent the Research Question for retrieving relevant documents: "
    return model.encode(instruction + query_text, normalize_embeddings=True).tolist()

# Функція виведення результатів
def print_results(results, title_text):
    print("\n" + "="*60)
    print(f" {title_text} ")
    print("="*60)
    matches = results.get("matches", [])
    if not matches:
        print("Статей не знайдено.")
    for idx, match in enumerate(matches):
        metadata = match.get("metadata", {})
        print(f"{idx+1}. ID: {match['id']} | Score: {match['score']:.4f}")
        print(f"   Назва: {metadata.get('title')}")
        print(f"   Категорія: {metadata.get('category')} | Рік: {metadata.get('year')}")
        print(f"   Абстракт: {metadata.get('abstract', '')[:150]}...")
        print("-" * 40)

# =====================================================================
# 3. Чистий семантичний пошук
# =====================================================================
query_1 = "teaching machines to recognize objects in pictures"
print(f"\nВиконуємо чистий пошук за запитом: '{query_1}'")
query_vector_1 = get_query_embedding(query_1)

results_1 = index.query(vector=query_vector_1, top_k=5, include_metadata=True)
print_results(results_1, "РЕЗУЛЬТАТИ ЧИСТОГО СЕМАНТИЧНОГО ПОШУКУ")


# =====================================================================
# 4. Пошук з фільтрацією метаданих (Суворо за ТЗ)
# =====================================================================
# ТЗ: "приклад A: статті по reinforcement learning за останні 5 років і категорія cs.LG"
query_task = "reinforcement learning" 

print(f"\nВиконуємо Приклад A: '{query_task}' (Рік >= 2021, категорія cs.LG)...")
query_vector_task = get_query_embedding(query_task)

results_A = index.query(
    vector=query_vector_task,
    top_k=5,
    include_metadata=True,
    filter={
        "year": {"$gte": 2021},
        "category": {"$eq": "cs.LG"}
    }
)
print_results(results_A, "ПРИКЛАД A: СУЧАСНІ СТАТТІ ПО REINFORCEMENT LEARNING")

# ТЗ: "приклад B: більш старі статті (до 2015 року), будь-яка категорія"
print(f"\nВиконуємо Приклад B: '{query_task}' (Рік <= 2015, будь-яка категорія)...")

results_B = index.query(
    vector=query_vector_task,
    top_k=5,
    include_metadata=True,
    filter={
        "year": {"$lte": 2015}
    }
)
print_results(results_B, "ПРИКЛАД B: ІСТОРИЧНІ СТАТТІ ПО REINFORCEMENT LEARNING")

# Порівняння видачі
print("\n" + "="*60)
print(" ПОРІВНЯННЯ ВИДАЧІ ТА ПОЯСНЕННЯ ВІДМІННОСТЕЙ ")
print("="*60)
print("Приклад A показує сучасні статті (від 2021 року), які сфокусовані виключно на домені cs.LG\n"
      "(Machine Learning). Тут ми бачимо що дані відсутні.\n"
      "Приклад B використовує той самий запит, але повертає фундаментальні та старі роботи (до 2015 року).\n"
      "Категорії тут можуть бути різними (наприклад, math.OC чи cs.AI).")

# =====================================================================
# 5. Порівняння різних метрик схожості на локальних ембеддингах
# =====================================================================
print("\n" + "="*60)
print(" РОЗРАХУНОК ТА ПОРІВНЯННЯ МЕТРИК ЛОКАЛЬНО ")
print("="*60)

if os.path.exists(INPUT_PARQUET) and os.path.exists(INPUT_EMBEDDINGS):
    df = pd.read_parquet(INPUT_PARQUET)
    local_embeddings = np.load(INPUT_EMBEDDINGS)
    
    # Використовуємо початковий запит query_1 за ТЗ
    q_vec = np.array(get_query_embedding(query_1))
    
    # Обчислення метрик за формулами
    dot_scores = np.dot(local_embeddings, q_vec)
    
    norm_embeddings = np.linalg.norm(local_embeddings, axis=1)
    norm_query = np.linalg.norm(q_vec)
    cosine_scores = dot_scores / (norm_embeddings * norm_query)
    
    l2_distances = np.linalg.norm(local_embeddings - q_vec, axis=1)
    
    # Топ-5 для кожної метрики
    top5_dot = np.argsort(dot_scores)[::-1][:5]
    top5_cosine = np.argsort(cosine_scores)[::-1][:5]
    top5_l2 = np.argsort(l2_distances)[:5]
    
    print(f"Запит для локального аналізу: '{query_1}'\n")
    print(f"{'№':<3} | {'Top-5 Dot Product':<25} | {'Top-5 Cosine Sim':<25} | {'Top-5 L2 Distance':<25}")
    print("-" * 78)
    for idx in range(5):
        # Формуємо красивий вивід з індексами датасету (наприклад, paper_4753)
        id_dot = f"paper_{top5_dot[idx]} (sc: {dot_scores[top5_dot[idx]]:.4f})"
        id_cos = f"paper_{top5_cosine[idx]} (sc: {cosine_scores[top5_cosine[idx]]:.4f})"
        id_l2 = f"paper_{top5_l2[idx]} (dist: {l2_distances[top5_l2[idx]]:.4f})"
      
        print(f"{idx+1:<3} | {id_dot:<25} | {id_cos:<25} | {id_l2:<25}")        
else:
    print("Локальні файли даних не знайдено.")