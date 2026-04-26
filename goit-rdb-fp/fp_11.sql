#1
CREATE SCHEMA pandemic;

USE pandemic;

SELECT count(*) FROM infectious_cases; # 10521

SELECT * FROM infectious_cases LIMIT 1000;

#2
SELECT DISTINCT Entity, Code FROM infectious_cases; # 245

CREATE TABLE infectious (
	infection_id INT AUTO_INCREMENT PRIMARY KEY,
    infection_name VARCHAR(50),
    infection_code VARCHAR(10)	
);

INSERT INTO infectious (infection_name, infection_code) SELECT DISTINCT Entity, Code FROM infectious_cases;

SELECT count(*) FROM infectious; # 245

SELECT * FROM infectious LIMIT 100;

CREATE TABLE infectious_data (
	infection_id INT,
	year int,
	number_yaws int,
	polio_cases int,
	cases_guinea_worm int,
	number_rabies decimal(20,7),
	number_malaria decimal(20,7),
	number_hiv decimal(20,7),
	number_tuberculosis decimal(20,7),
	number_smallpox decimal(20,7),
	number_cholera_cases decimal(20,7)
);

INSERT INTO infectious_data (
	infection_id,
	year,
    number_yaws,
    polio_cases,
    cases_guinea_worm,
    number_rabies,
    number_malaria,
    number_hiv,
    number_tuberculosis,
    number_smallpox,
    number_cholera_cases
) 
SELECT 
	i.infection_id,
    COALESCE(NULLIF(TRIM(ic.Year), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.number_yaws), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.polio_cases), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.cases_guinea_worm), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.Number_rabies), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.Number_malaria), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.Number_hiv), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.Number_tuberculosis), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.Number_smallpox), ''), '0'),
    COALESCE(NULLIF(TRIM(ic.Number_cholera_cases), ''), '0')
FROM infectious_cases ic
LEFT JOIN infectious i ON ic.Entity = i.infection_name;

SELECT count(*) FROM pandemic.infectious_data;  # 10521

SELECT * FROM pandemic.infectious_data LIMIT 1000;

#3
SELECT 
	infection_name entity, 
    infection_code code,
    avg(number_rabies) avg_number_rabies,
    min(number_rabies) min_number_rabies,
    max(number_rabies) max_number_rabies
FROM infectious_data id
LEFT JOIN infectious i ON id.infection_id = i.infection_id
GROUP BY infection_name, infection_code
ORDER BY avg_number_rabies DESC
LIMIT 10;

#4
SELECT 
	year,
	year_date,
    curr_date,
    TIMESTAMPDIFF(YEAR, year_date, curr_date) year_diff
FROM (
	SELECT 
		year,
		MAKEDATE(year,1) year_date,
		CURDATE() curr_date
	FROM infectious_data id
) t;

#5
DELIMITER //
CREATE FUNCTION CalculateYearDiff(year_in INT)
RETURNS INT
DETERMINISTIC 
NO SQL
BEGIN
    IF year_in IS NULL THEN
        RETURN NULL;
    END IF;
    IF year_in = 0 THEN
		RETURN YEAR(CURDATE());
	END IF;
	RETURN TIMESTAMPDIFF(YEAR, MAKEDATE(year_in, 1), CURDATE());
END //
DELIMITER ;

SELECT 
	year,
    CalculateYearDiff(year) year_diff
FROM infectious_data id;
