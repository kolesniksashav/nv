-- 3
-- Напишіть запит за допомогою операторів FROM та INNER JOIN, що об’єднує всі таблиці даних
SELECT
	ct.`id` category_id,
    ct.`name` category_name,
    ct.`description` category_description,
	p.`id` product_id,
    p.`name` product_name,
    p.`supplier_id` product_supplier_id,
    p.`category_id` product_category_id,
    p.`unit` product_unit,
    p.`price` product_price,
	s.`id` supplier_id,
    s.`name` supplier_name,
    s.`contact` supplier_contact,
    s.`address` supplier_address,
    s.`city` supplier_city,
    s.`postal_code` supplier_postal_code,
    s.`country` supplier_country,
    s.`phone` supplier_phone,
	od.`id` order_detail_id,
    od.`order_id` order_detail_order_id,
    od.`product_id` order_detail_product_id,
    od.`quantity` order_detail_quantity,
	o.`id` order_id,
    o.`customer_id` order_customer_id,
    o.`employee_id` order_employee_id,
    o.`date` order_date,
    o.`shipper_id` order_shipper_id,
    sh.`id` shipper_id,
    sh.`name` shipper_name,
    sh.`phone` shipper_phone,
	e.`employee_id`,
    e.`last_name` employee_last_name,
    e.`first_name` employee_first_name,
    e.`birthdate` employee_birthdate,
    e.`photo` employee_photo,
    e.`notes` employee_notes,
	c.`id` customer_id,
    c.`name` customer_name,
    c.`contact` customer_contact,
    c.`address` customer_address,
    c.`city` customer_city,
    c.`postal_code` customer_postel_code,
    c.`country` customer_country
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id;
-- 4.1
-- Визначте, скільки рядків ви отримали (за допомогою оператора COUNT).
SELECT count(*)
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id;
-- 4.2
-- Змініть декілька операторів INNER на LEFT чи RIGHT. 
-- Визначте, що відбувається з кількістю рядків. Чому? Напишіть відповідь у текстовому файлі.
SELECT count(*)
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
RIGHT JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
LEFt JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id;
-- 4.3
-- На основі запита з пункта 3 виконайте наступне: оберіть тільки ті рядки, де employee_id > 3 та ≤ 10.
SELECT count(*)
FROM mydb.categories ct 
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id
WHERE e.employee_id between 3 and 10;
-- 4.4 
-- Згрупуйте за іменем категорії, порахуйте кількість рядків у групі, 
-- середню кількість товару (кількість товару знаходиться в order_details.quantity)
SELECT 
	ct.name category_name,
    count(*) category_lines,
    avg(od.quantity) avg_category_quantity
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id
WHERE e.employee_id between 3 and 10
GROUP BY ct.name;
-- 4.5
-- Відфільтруйте рядки, де середня кількість товару більша за 21.
SELECT 
	ct.name category_name,
    count(*) category_lines,
    avg(od.quantity) avg_category_quantity
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id
WHERE e.employee_id between 3 and 10
GROUP BY ct.name
HAVING avg_category_quantity > 21;
-- 4.6
-- Відсортуйте рядки за спаданням кількості рядків.
SELECT 
	ct.name category_name,
    count(*) category_lines,
    avg(od.quantity) avg_category_quantity
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id
WHERE e.employee_id between 3 and 10
GROUP BY ct.name
HAVING avg_category_quantity > 21
ORDER BY category_lines DESC;
-- 4.7
-- Виведіть на екран (оберіть) чотири рядки з пропущеним першим рядком.
SELECT 
	ct.name category_name,
    count(*) category_lines,
    avg(od.quantity) avg_category_quantity
FROM mydb.categories ct
INNER JOIN mydb.products p
ON p.category_id = ct.id
INNER JOIN mydb.suppliers s
ON p.supplier_id = s.id
INNER JOIN mydb.order_details od
ON od.product_id = p.id
INNER JOIN mydb.orders o
ON o.id = od.order_id
INNER JOIN mydb.shippers sh
ON sh.id = o.shipper_id
INNER JOIN mydb.employees e
ON e.employee_id = o.employee_id
INNER JOIN mydb.customers c
ON c.id = o.customer_id
WHERE e.employee_id between 3 and 10
GROUP BY ct.name
HAVING avg_category_quantity > 21
ORDER BY category_lines DESC
LIMIT 4 OFFSET 1;