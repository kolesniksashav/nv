import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

INPUT_PARQUET = "data/arxiv_subset.parquet"
INPUT_EMBEDDINGS = "embeddings/embeddings.npy"
INDEX_NAME = "arxiv-papers"
VECTOR_DIM = 768
BATCH_SIZE = 200   # Pinecone рекомендує батчі до 200 векторів

# Перевірка наявності API ключа
if "PINECONE_API_KEY" not in os.environ:
    raise ValueError("Помилка: PINECONE_API_KEY не знайдено в змінних оточення (.env файл).")

# Ініціалізація клієнта
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# 1. Створюємо індекс (якщо не існує) і підключаємося до нього
print(f"Перевірка наявності індексу '{INDEX_NAME}'...")
existing_indexes = [index.name for index in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    print(f"Індекс '{INDEX_NAME}' не знайдено. Створення нового індексу...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=VECTOR_DIM,
        # Оскільки ембеддинги нормалізовані (довжина = 1.0), 
        # використовуємо надшвидку метрику dotproduct (скалярний добуток)
        metric="dotproduct", 
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"  # Безкоштовний tier Pinecone зазвичай використовує цей регіон
        )
    )
    print(f"Індекс '{INDEX_NAME}' успішно створено.")
else:
    print(f"Індекс '{INDEX_NAME}' вже існує. Підключення...")

# Підключаємося до індексу
index = pc.Index(INDEX_NAME)

# 2. Завантаження локальних даних
print(f"Читання датасету з {INPUT_PARQUET}...")
df = pd.read_parquet(INPUT_PARQUET)

print(f"Завантаження ембеддингів з {INPUT_EMBEDDINGS}...")
embeddings = np.load(INPUT_EMBEDDINGS)

# Перевірка на відповідність розмірів
if len(df) != len(embeddings):
    raise ValueError(f"Невідповідність розмірів! Датасет має {len(df)} рядків, а матриця ембеддингів — {len(embeddings)}.")

# 3. Підготовка даних та 4. Завантаження в Pinecone батчами
total_records = len(df)
print(f"Початок підготовки та завантаження {total_records} векторів...")

# Використовуємо tqdm для гарного відображення прогресу завантаження батчів
for i in tqdm(range(0, total_records, BATCH_SIZE), desc="Завантаження в Pinecone"):
    batch_end = min(i + BATCH_SIZE, total_records)
    
    # Зрізи для поточного батчу
    df_batch = df.iloc[i:batch_end]
    emb_batch = embeddings[i:batch_end]
    
    upsert_data = []
    
    for idx, (index_label, row) in enumerate(df_batch.iterrows()):
        # Формуємо унікальний id (використовуємо глобальний індекс i + idx)
        global_idx = i + idx
        paper_id = f"paper_{global_idx}"
        
        # Обробка та лімітування метаданих
        title = str(row.get("title", ""))
        abstract = str(row.get("abstract", ""))
        authors = str(row.get("authors", ""))
        
        # Конвертуємо рік до int, якщо це можливо (щоб Pinecone міг фільтрувати за числовим значенням)
        try:
            year = int(row.get("year"))
        except (ValueError, TypeError):
            year = 0
            
        metadata = {
            "arxiv_id": str(row.get("id", row.get("arxiv_id", ""))),
            "title": title,
            "abstract": abstract[:500],  # Обрізання до 500 символів
            "authors": authors[:200],    # Обрізання до 200 символів
            "year": year,
            "category": str(row.get("categories", row.get("category", "")))
        }
        
        # Кожен елемент батчу — це кортеж (id, vector, metadata)
        upsert_data.append((paper_id, emb_batch[idx].tolist(), metadata))
    
    # Відправляємо батч в індекс Pinecone
    index.upsert(vectors=upsert_data)

print("\nЗавантаження повністю завершено!")

# 5. Виведення загальної кількості векторів в індексі
index_stats = index.describe_index_stats()
total_vectors = index_stats["total_vector_count"]
print("="*40)
print(f"Загальна кількість векторів в індексі '{INDEX_NAME}': {total_vectors}")
print("="*40)