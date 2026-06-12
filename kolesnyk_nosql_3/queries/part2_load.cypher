// Дані розміщено на Google Drive.

// ============================================================================
// ЧАСТИНА 2.1: ЗАВАНТАЖЕННЯ ВУЗЛІВ (NODES)
// ============================================================================

// 1. Імпорт унікальних жанрів (Genre)

LOAD CSV WITH HEADERS FROM 'https://docs.google.com/uc?export=download&id=nodes_genre_csv_id' AS row
MERGE (g:Genre {name: row.name});

// 2. Імпорт користувачів (User)

LOAD CSV WITH HEADERS FROM 'https://docs.google.com/uc?export=download&id=nodes_user_csv_id' AS row
MERGE (u:User {userId: toInteger(row.userId)})
ON CREATE SET u.gender = row.gender,
              u.age = toInteger(row.age),
              u.occupation = toInteger(row.occupation);

// 3. Імпорт фільмів (Movie)

LOAD CSV WITH HEADERS FROM 'https://docs.google.com/uc?export=download&id=nodes_movie_csv_id' AS row
MERGE (m:Movie {movieId: toInteger(row.movieId)})
ON CREATE SET m.title = row.title,
              m.year = toInteger(row.year);

// ============================================================================
// ЧАСТИНА 2.2: СТВОРЕННЯ ІНДЕКСІВ ТА ОБМЕЖЕНЬ (CONSTRAINTS)
// ============================================================================

// Створення обмеження унікальності для User (автоматично створює індекс)
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.userId IS UNIQUE;

// Створення обмеження унікальності для Movie (автоматично створює індекс)
CREATE CONSTRAINT movie_id_unique IF NOT EXISTS
FOR (m:Movie) REQUIRE m.movieId IS UNIQUE;

// Створення звичайного індексу для Genre за назвою для швидкого текстового пошуку
CREATE INDEX genre_name_index IF NOT EXISTS
FOR (g:Genre) ON (g.name);

// ============================================================================
// ЧАСТИНА 2.3: ЗАВАНТАЖЕННЯ РЕБЕР (EDGES)
// ============================================================================

// 1. Створення зв'язків HAS_GENRE (Фільм -> Жанр)

LOAD CSV WITH HEADERS FROM 'https://docs.google.com/uc?export=download&id=edges_has_genre_csv_id' AS row
MATCH (m:Movie {movieId: toInteger(row.movieId)})
MATCH (g:Genre {name: row.name})
MERGE (m)-[:HAS_GENRE]->(g);

// 2. Створення зв'язків RATED (Користувач -> Оцінка -> Фільм) через APOC батчі по 10 000 рядків
//Procedure apoc.periodic.iterate is deprecated. Alternative: Cypher's CALL {...} IN TRANSACTIONS.
//CALL subquery without a variable scope clause is deprecated. Use CALL (row) { ... }

LOAD CSV WITH HEADERS FROM 'https://docs.google.com/uc?export=download&id=edges_rated_csv_id' AS row
CALL (row) {
  MATCH (u:User {userId: toInteger(row.userId)})
  MATCH (m:Movie {movieId: toInteger(row.movieId)})
  MERGE (u)-[r:RATED]->(m)
  ON CREATE SET r.rating = toInteger(row.rating),
                r.timestamp = toInteger(row.timestamp)
} IN TRANSACTIONS OF 10000 ROWS; // за замовчуванням тут діє ASYNCHRONOUS/CONCURRENT FALSE


