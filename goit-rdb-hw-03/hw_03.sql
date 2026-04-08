USE mydb;
# 1
SELECT * FROM mydb.products;
SELECT name, phone FROM mydb.shippers;
# 2
# SELECT * FROM mydb.products ORDER BY price desc LIMIT 1;
SELECT round(avg(price), 2) avg_price, max(price) max_price, min(price) min_price FROM mydb.products;
# 3
SELECT distinct category_id, price FROM mydb.products ORDER BY category_id;
# 4
SELECT count(*) FROM mydb.products WHERE price between 20 and 100;
# 5
SELECT supplier_id, count(*) product_count, round(avg(price), 2) avg_price FROM mydb.products GROUP BY supplier_id;