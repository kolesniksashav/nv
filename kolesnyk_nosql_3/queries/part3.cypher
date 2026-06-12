// ============================================================================
// ЧАСТИНА 3: Запити різної складності
// ============================================================================

//Запит 1. Знайти всі фільми жанру «Thriller» із середнім рейтингом вище 4.0:
 
MATCH (g:Genre {name: "Thriller"})<-[:HAS_GENRE]-(m:Movie)<-[r:RATED]-()
WITH m, round(avg(r.rating), 2) AS AvgRating, count(r) AS TotalRatings
WHERE AvgRating > 4.0
RETURN m.movieId AS MovieID, 
       m.title AS Title, 
       m.year AS ReleaseYear,
       AvgRating AS AverageRating, 
       TotalRatings AS VoteCount
ORDER BY AverageRating DESC, VoteCount DESC;

//Запит 2. Знайти користувачів, які поставили оцінку 5 більш ніж 50 фільмам: 

MATCH (u:User)-[r:RATED]->(:Movie)
WHERE r.rating = 5
WITH u, count(r) AS HighRatingCount
WHERE HighRatingCount > 50
RETURN u.userId AS UserID, 
       HighRatingCount AS TotalFiveStarRatings
ORDER BY TotalFiveStarRatings DESC;

// Запит 3. Знайти фільми, які обидва користувачі (наприклад, userId=1 і userId=2) оцінили високо (рейтинг ≥ 4):

MATCH (u1:User {userId: 1})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User {userId: 2})
WHERE r1.rating >= 4 AND r2.rating >= 4
RETURN m.movieId AS MovieID, 
       m.title AS Title, 
       m.year AS ReleaseYear,
       r1.rating AS User1Rating, 
       r2.rating AS User2Rating;

// Запит 4. Знайти жанри, чиї фільми стабільно отримують високі оцінки — середній рейтинг і кількість оцінок:

MATCH (g:Genre)<-[:HAS_GENRE]-(m:Movie)<-[r:RATED]-()
WITH g, round(avg(r.rating), 2) AS GenreAvgRating, count(r) AS TotalGenreRatings
WHERE TotalGenreRatings > 1000
RETURN g.name AS GenreName, 
       GenreAvgRating AS AverageRating, 
       TotalGenreRatings AS VoteCount
ORDER BY AverageRating DESC, VoteCount DESC
LIMIT 5;

// Запит 5. Рекомендація «користувачі зі схожими смаками також дивилися»: для заданого користувача знайти фільми, які він ще не дивився, але високо оцінили користувачі з подібними смаками:

// 1. Знаходимо нашого користувача (userId: 1) та інших людей, які оцінили ТІ САМІ фільми
MATCH (u:User {userId: 1})-[r1:RATED]->(m:Movie)<-[r2:RATED]->(other:User)
// 2. Рахуємо різницю в оцінках для кожного спільного фільму та кількість перетинів
WITH u, other, count(m) AS SharedMoviesCount, avg(abs(r1.rating - r2.rating)) AS AvgRatingDifference
// ФІЛЬТР СХОЖОСТІ: мінімум 3 спільні фільми, і середня розбіжність в оцінках не більша за 0.75
WHERE SharedMoviesCount >= 3 AND AvgRatingDifference <= 0.75
// 3. Для знайдених "споріднених душ" шукаємо фільми, які вони оцінили високо (4 або 5)
MATCH (other)-[r3:RATED]->(recMovie:Movie)
WHERE r3.rating >= 4
// 4. ЗАХИСТ: Перевіряємо, щоб наш Користувач №1 ще НЕ дивився цей фільм
AND NOT (u)-[:RATED]->(recMovie)
// 5. Агрегуємо рекомендації та підраховуємо метрики
WITH recMovie, avg(r3.rating) AS PredictedRating, count(DISTINCT other) AS RecommendedByUsersCount
RETURN recMovie.movieId AS MovieID, 
       recMovie.title AS Title, 
       recMovie.year AS ReleaseYear,
       round(PredictedRating, 2) AS ExpectedRating, 
       RecommendedByUsersCount AS SimilarUsersCount
// Сортуємо: спочатку показуємо те, що рекомендує НАЙБІЛЬША кількість схожих людей, 
// а при збігу — де вищий прогнозований бал
ORDER BY SimilarUsersCount DESC, ExpectedRating DESC
LIMIT 10;

// Запит 6. Знайти найкоротший ланцюжок зв’язку між двома користувачами через спільні фільми:

MATCH (u1:User {userId: 1})
WITH u1
MATCH (u2:User {userId: 99})
MATCH p = shortestPath((u1)-[:RATED*..10]-(u2))
RETURN p;
