use mydb;
# 1
SELECT 
	*,
    (SELECT customer_id FROM orders WHERE od.order_id = id) customer_id
FROM order_details od;
# 2
SELECT *
FROM order_details od
WHERE order_id IN (SELECT id FROM orders WHERE shipper_id = 3);
# 3
SELECT order_id, AVG(quantity) avg_quantity
FROM (SELECT * FROM order_details WHERE quantity > 10) t1
GROUP BY order_id;
# 4
WITH t2 AS (
	SELECT * FROM order_details WHERE quantity > 10
)
SELECT order_id, AVG(quantity) avg_quantity
FROM t2
GROUP BY order_id;
# 5
DELIMITER //
CREATE FUNCTION CalculateCustPercentage(param1 FLOAT, param2 FLOAT)
RETURNS FLOAT
DETERMINISTIC 
NO SQL
BEGIN
	DECLARE result FLOAT;
	SET result = param1 / param2;
	RETURN result;
END //
DELIMITER ;

SELECT 
	*,
    CalculateCustPercentage(quantity,2) CustPers
FROM order_details;

DROP FUNCTION IF EXISTS CalculateCustPercentage;