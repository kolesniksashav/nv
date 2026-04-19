use mydb;
# 1
SELECT
	id,
    date,
    year(date) year_date,
    month(date) month_date,
    day(date) day_date
FROM mydb.orders;
#2
SELECT
	id,
    date,
    date + interval 1 day  increased_day
FROM mydb.orders;
#3
SELECT
	id,
    date,
    round(UNIX_TIMESTAMP(date),0) secs_from_begining
FROM mydb.orders;
#4
SELECT 
	count(*)
FROM mydb.orders
WHERE date between '1996-07-10 00:00:00' and '1996-10-08 00:00:00';
#5
SELECT 
	id, 
    date, 
    JSON_OBJECT("id", id, "date", date) AS created_json_object
FROM mydb.orders;