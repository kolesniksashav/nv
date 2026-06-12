import re
import pandas as pd

folder = "ml-1m"
destination = "import"
# ==========================================
# 1. КОНВЕРТАЦІЯ USERS (Вузли Користувачів)
# ==========================================
print("Обробка вузлів User...")
users = pd.read_csv(
    f"{folder}/users.dat", 
    sep="::", 
    engine="python", 
    names=["userId", "gender", "age", "occupation", "zipCode"], # zipCode ігноруємо або лишаємо
    encoding="latin-1"
)
# Зберігаємо лише ті колонки, які вказані у вашій підказці
users_nodes = users[["userId", "gender", "age", "occupation"]]
users_nodes.to_csv(f"{destination}/nodes_user.csv", index=False)


# ==========================================
# 2. ОБРОБКА MOVIES ТА GENRES (Вузли та зв'язки)
# ==========================================
print("Обробка вузлів Movie, Genre та зв'язків HAS_GENRE...")
movies_raw = pd.read_csv(
    f"{folder}/movies.dat", 
    sep="::", 
    engine="python", 
    names=["movieId", "title_raw", "genres_raw"],
    encoding="latin-1"
)

# Функція для витягування року, наприклад: "Toy Story (1995)" -> 1995
def extract_year(title):
    match = re.search(r'\((\d{4})\)$', title.strip())
    if match:
        return int(match.group(1))
    return None # якщо раптом року немає

# Функція для очищення назви від року: "Toy Story (1995)" -> "Toy Story"
def clean_title(title):
    return re.sub(r'\s*\(\d{4}\)$', '', title).strip()

movies_raw['year'] = movies_raw['title_raw'].apply(extract_year)
movies_raw['title'] = movies_raw['title_raw'].apply(clean_title)

# Створюємо фінальну таблицю для вузлів Movie
movies_nodes = movies_raw[["movieId", "title", "year"]]
movies_nodes.to_csv(f"{destination}/nodes_movie.csv", index=False)

# Збираємо унікальні жанри для вузлів Genre та зв'язків
genres_set = set()
edges_has_genre = []

for _, row in movies_raw.iterrows():
    # Жанри розділені рискою '|', наприклад: "Animation|Children's|Comedy"
    movie_genres = row['genres_raw'].split('|')
    for g in movie_genres:
        genres_set.add(g)
        # Додаємо пару для зв'язку (Movie)-[:HAS_GENRE]->(Genre)
        edges_has_genre.append({"movieId": row["movieId"], "name": g})

# Створюємо файл вузлів Genre
genre_nodes = pd.DataFrame({"name": list(genres_set)})
genre_nodes.to_csv(f"{destination}/nodes_genre.csv", index=False)

# Створюємо файл зв'язків HAS_GENRE
edges_has_genre_df = pd.DataFrame(edges_has_genre)
edges_has_genre_df.to_csv(f"{destination}/edges_has_genre.csv", index=False)


# ==========================================
# 3. КОНВЕРТАЦІЯ RATINGS (Зв'язки RATED)
# ==========================================
print("Обробка зв'язків RATED...")
ratings = pd.read_csv(
    f"{folder}/ratings.dat", 
    sep="::", 
    engine="python", 
    names=["userId", "movieId", "rating", "timestamp"],
    encoding="latin-1"
)
# Вони вже ідеально підходять під структуру (User)-[:RATED]->(Movie)
ratings.to_csv(f"{destination}/edges_rated.csv", index=False)

print("\nВсі файли підготовлено для графової структури!")