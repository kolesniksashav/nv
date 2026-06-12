// 5.1. PageRank на графі фільмів

// Крок 1: матеріалізуємо ребра фільм-фільм через спільних користувачів
MATCH (m1:Movie)<-[r1:RATED]-(u:User)-[r2:RATED]->(m2:Movie)
WHERE r1.rating >= 4 AND r2.rating >= 4 AND elementId(m1) < elementId(m2)
WITH m1, m2, count(u) AS weight
WHERE size([(m1)<-[:RATED]-() | 1]) > 20
AND size([(m2)<-[:RATED]-() | 1]) > 20
WITH m1, m2, weight
ORDER BY weight DESC
LIMIT 50000
MERGE (m1)-[co:CO_RATED]-(m2)
SET co.weight = weight;

// Крок 2: створюємо проєкцію на основі матеріалізованих ребер
CALL gds.graph.project(
  'movieGraph',                      // Назва проєкції
  'Movie',                           // Мітка вузлів (з урахуванням вашої структури Movie2)
  ['CO_RATED'],                      // Список типів зв'язків (як масив рядків)
  {                                  // Об'єкт конфігурації (настройка властивостей)
    relationshipProperties: ['weight'], // Властивість ребра
    memory: '2GB'                    // Виділяємо мінімально доступний хмарний пакет пам'яті
  }
)
YIELD graphName, nodeCount, relationshipCount;

// Крок 3: Запуск алгоритму PageRank на створеній проєкції 'movieGraph'
CALL gds.pageRank.stream('movieGraph', {
  maxIterations: 20,
  dampingFactor: 0.85,
  relationshipWeightProperty: 'weight'
})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS m, score
RETURN m.title AS Title, 
       m.year AS ReleaseYear, 
       round(score, 2) AS PageRankScore
ORDER BY PageRankScore DESC
LIMIT 10;

// Крок 4: видаляємо проєкцію та тимчасові ребра
CALL gds.graph.drop('movieGraph');
MATCH ()-[co:CO_RATED]-() DELETE co;


// 5.2. Виявлення спільнот (Louvain)

// Крок 1: матеріалізуємо ребра користувач-користувач через спільні фільми
// 1. Знаходимо ВСІХ унікальних користувачів, у яких є хоч одна оцінка >= 4
MATCH (u:User)-[r:RATED]->()
WHERE r.rating >= 4
WITH DISTINCT u

// 2. Передаємо їх поштучно (пачками по 1 людині) в конвеєр
CALL (u) {
  // Шукаємо пари для ОДНОГО конкретного користувача 'u'
  MATCH (u)-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User)
  WHERE r1.rating >= 4 AND r2.rating >= 4 
    AND elementId(u) < elementId(u2)
  
  WITH u, u2, count(m) AS weight // бере всі знайдені фільми-збіги для цієї конкретної пари людей і підраховує їхню загальну кількість

  // Записуємо ребро SIMILAR
  MERGE (u)-[sim:SIMILAR]->(u2)
  SET sim.weight = weight
} IN TRANSACTIONS OF 1 ROWS; // Рятуємо RAM: обробляємо строго по одному користувачу

// Крок 2: створюємо проєкцію на основі матеріалізованих ребер
CALL gds.graph.project(
  'userSimilarity',                  // Назва проєкції
  'User',                            // Мітка вузлів (з урахуванням вашої структури Movie)
  ['SIMILAR'],                       // Список типів зв'язків (як масив рядків)
  {                                  // Об'єкт конфігурації (настройка властивостей)
    relationshipProperties: ['weight'], // Властивість ребра
    memory: '2GB'                    // Виділяємо мінімально доступний хмарний пакет пам'яті
  }
)
YIELD graphName, nodeCount, relationshipCount;

// Крок 3: Запуск Louvain у режимі mutate, властивість створюється всередині проєкції
CALL gds.louvain.mutate('userSimilarity', {
  mutateProperty: 'louvainCommunity', 
  relationshipWeightProperty: 'weight',
  maxLevels: 10,
  maxIterations: 10
})
YIELD communityCount, modularity, modularities;

// Крок 4: Дістаємо результати Louvain з пам'яті проєкції та аналізуємо жанри
CALL gds.graph.nodeProperty.stream('userSimilarity', 'louvainCommunity')
YIELD nodeId, propertyValue AS communityId

// Знаходимо реальні вузли користувачів за їхніми внутрішніми ID
WITH gds.util.asNode(nodeId) AS u, communityId
WHERE u:User

// Рахуємо розмір кожного кластера
WITH communityId, count(u) AS clusterSize
ORDER BY clusterSize DESC
LIMIT 10

// Для ТОП-10 кластерів дістаємо користувачів та їхні улюблені жанри з бази даних
MATCH (u2:User)-[r:RATED]->(m:Movie)-[:HAS_GENRE]->(g:Genre)
// Зв'язуємо користувачів з їхніми кластерами що знаходяться в пам'яті
WHERE gds.graph.nodeProperty.stream('userSimilarity', 'louvainCommunity', elementId(u2)) = communityId AND r.rating >= 4
WITH communityId, clusterSize, g.name AS genreName, count(m) AS genreVotes
ORDER BY communityId, genreVotes DESC

// Формуємо фінальний звіт
WITH communityId, clusterSize, collect({genre: genreName, votes: genreVotes}) AS sortedGenres
RETURN communityId AS CommunityID,
       clusterSize AS UsersCount,
       sortedGenres[0].genre + " (" + sortedGenres[0].votes + ")" AS Top1_Genre,
       sortedGenres[1].genre + " (" + sortedGenres[1].votes + ")" AS Top2_Genre,
       sortedGenres[2].genre + " (" + sortedGenres[2].votes + ")" AS Top3_Genre
ORDER BY UsersCount DESC;

// 1. Видаляємо проекцію
CALL gds.graph.drop('userSimilarity', false); // Режим м'якого видалення

// 2. Знаходимо абсолютно всі існуючі ребра SIMILAR на диску
MATCH ()-[sim:SIMILAR]-() 

// 3. Явно передаємо змінну 'sim' у область видимості підзапиту (Variable Scope)
CALL (sim) {
  DELETE sim
} IN TRANSACTIONS OF 10000 ROWS; // Видаляємо пачками для економії RAM


// 5.3. Найкоротший шлях між користувачами

// Крок 1: створюємо проєкцію на основі матеріалізованих ребер
CALL gds.graph.project(
  'userGraph',                      // Назва вашої проєкції
  'User',                          // Мітка вузлів
  ['SIMILAR'],                      // Назва ребра як рядок у списку (виправляє першу помилку)
  {
    undirectedRelationshipTypes: ['SIMILAR'], // Встановлюємо зв'язок як неорієнтований для Дейкстра
    relationshipProperties: ['weight'], // Властивість ребра
    memory: '2GB'                    // Виділяємо мінімально доступний хмарний пакет пам'яті
  }
)

// Крок 2: Шукаємо найкоротший шлях за допомогою Дейкстра
MATCH (source:User {userId: 1})
WITH source
MATCH (target:User {userId: 4300})
WITH source, target
CALL gds.shortestPath.dijkstra.stream('userGraph', {
  sourceNode: source,
  targetNode: target,
  relationshipWeightProperty: 'weight'
})
YIELD nodeIds, totalCost
RETURN
  totalCost,
  [nodeId IN nodeIds | gds.util.asNode(nodeId).userId] AS route;

// Крок 3: Видалення проекції
CALL gds.graph.drop('userGraph');
