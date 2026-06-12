// Крок 1. Знайдіть вузли з аномально великою кількістю ребер:

MATCH (n)
WITH n, COUNT { (n)--() } AS degree
WHERE degree > 1000
RETURN labels(n) AS NodeLabels, 
       coalesce(n.title, n.userId, n.name) AS Identifier, 
       degree
ORDER BY degree DESC
LIMIT 20;

// Окремо для кожного з вузлів:

// 1. Шукаємо ТОП-5 супервузлів серед ЖАНРІВ
MATCH (g:Genre)
WITH g, COUNT { (g)--() } AS degree
WITH g, degree
ORDER BY degree DESC
LIMIT 5
RETURN "Жанр" AS Type, g.name AS Identifier, degree

UNION

// 2. Шукаємо ТОП-5 супервузлів серед ФІЛЬМІВ
MATCH (m:Movie)
WITH m, COUNT { (m)--() } AS degree
WITH m, degree
ORDER BY degree DESC
LIMIT 5
RETURN "Фільм" AS Type, m.title + " (" + m.year + ")" AS Identifier, degree

UNION

// 3. Шукаємо ТОП-5 супервузлів серед КОРИСТУВАЧІВ
MATCH (u:User)
WITH u, COUNT { (u)--() } AS degree
WITH u, degree
ORDER BY degree DESC
LIMIT 5
RETURN "Користувач (ID)" AS Type, toString(u.userId) AS Identifier, degree

ORDER BY degree DESC;