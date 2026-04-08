CREATE SCHEMA LibraryManagement;

USE LibraryManagement;
CREATE TABLE authors (
	author_id INT AUTO_INCREMENT PRIMARY KEY,
	author_name VARCHAR(255)
);

CREATE TABLE genres (
	genre_id INT AUTO_INCREMENT PRIMARY KEY,
	genre_name VARCHAR(255)
);

CREATE TABLE books (
	book_id INT AUTO_INCREMENT PRIMARY KEY,
	title VARCHAR(255), 
    publication_year YEAR,
	author_id INT,
	FOREIGN KEY (author_id) REFERENCES authors(author_id),
	genre_id INT,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

CREATE TABLE users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(255),
    email VARCHAR(150)
);

CREATE TABLE borrowed_books (
	borrow_id INT AUTO_INCREMENT PRIMARY KEY,
	book_id INT,
	FOREIGN KEY (book_id) REFERENCES books(book_id),
	user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    borrow_date DATE,
    return_date DATE
);

-- 1. Додаємо авторів
INSERT INTO authors (author_name) 
VALUES ('Джордж Орвелл'), ('Ліна Костенко');

-- 2. Додаємо жанри
INSERT INTO genres (genre_name) 
VALUES ('Антиутопія'), ('Поезія');

-- 3. Додаємо книги (зв'язуємо з авторами та жанрами через ID)
INSERT INTO books (title, publication_year, author_id, genre_id) 
VALUES 
('1984', 1949, 1, 1), -- автор_id 1 (Орвелл), жанр_id 1 (Антиутопія)
('Маруся Чурай', 1979, 2, 2); -- автор_id 2 (Костенко), жанр_id 2 (Поезія)

-- 4. Додаємо користувачів
INSERT INTO users (username, email) 
VALUES 
('ivan_petrov', 'ivan@example.com'),
('olena_books', 'olena@test.ua');

-- 5. Додаємо записи про видачу книг
-- Використовуємо book_id та user_id, які вже існують у базі
INSERT INTO borrowed_books (book_id, user_id, borrow_date, return_date) 
VALUES 
(1, 1, '2024-05-01', '2024-05-15'), -- Іван взяв "1984"
(2, 2, '2024-05-10', NULL);          -- Олена взяла "Маруся Чурай" і ще не повернула

