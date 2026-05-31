import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

def main():
    # 1. Завантажити датасет із файлу data/arxiv_subset.parquet
    input_path = "data/arxiv_subset.parquet"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл {input_path} не знайдено. Будь ласка, перевірте крок підготовки даних.")
    
    print(f"Завантаження датасету з {input_path}...")
    df = pd.read_parquet(input_path)
    
    # 2. Підготувати тексти для кодування: об’єднання title і abstract через [SEP]
    print("Підготовка текстів для кодування...")
    # Використовуємо .fillna(""), щоб уникнути помилок, якщо якесь поле виявиться пустим
    texts = df['title'].fillna("") + " [SEP] " + df['abstract'].fillna("")
    texts = texts.tolist()
    
    # 3. Ініціалізація моделі allenai/specter2_base
    print("Завантаження моделі allenai/specter2_base...")
    # sentence-transformers автоматично завантажить модель з HuggingFace та використає GPU (CUDA), якщо вона доступна
    model = SentenceTransformer("allenai/specter2_base")
    
    # 4. Генерування ембеддингів з урахуванням вимог:
    # batch_size=64, show_progress_bar=True (відображення прогресу), normalize_embeddings=True (нормалізація)
    print(f"Генерування ембеддингів для {len(texts)} текстів (розмір батчу: 64)...")
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    
    # 5. Виведення метрик в консоль
    print("\n" + "="*40)
    print("СТАТИСТИКА ОТРИМАНИХ ЕМБЕДДИНГІВ:")
    print("="*40)
    # Загальна кількість оброблених текстів
    print(f"Загальна кількість оброблених текстів: {embeddings.shape[0]}")
    # Розмірність ембеддингів (очікується 768)
    print(f"Розмірність ембеддингів: {embeddings.shape[1]}")
    
    # Норма першого ембеддингу (L2-норма vector)
    first_embedding_norm = np.linalg.norm(embeddings[0])
    print(f"Норма першого ембеддингу: {first_embedding_norm:.6f} (очікується близька до 1.0)")
    print("="*40 + "\n")
    
    # 6. & 7. Перевірка директорії та збереження ембеддингів у форматі NumPy
    output_dir = "embeddings"
    output_path = os.path.join(output_dir, "embeddings.npy")
    
    # Перед збереженням переконуємося, що директорія існує
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Збереження ембеддингів у файл {output_path}...")
    np.save(output_path, embeddings)
    print("Успішно збережено!")

if __name__ == "__main__":
    main()