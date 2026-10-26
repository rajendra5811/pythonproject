-- 15 UPDATE phone AS 1000000 FOR RAVI
UPDATE EMP1 SET phone = 1000000
WHERE name ='RAVI' AND phone is null

-- 16. AND, OR, NOT IN SQL

--AND -IF WE HAVE 2 CONDITION THEN BOTH CONDITION IF ITS MATCHING THEN WE WILL GET RESULT
--OR/IN-IF WE HAVE 2 CONDITION AND IF ANY OF THE CONDITION SATISFY THEN WE WILL GET RESULT
--NOT --IF CONDITION WE ARE CHECKING WITH NOT CLAUSE

-- GIVE EMPLOYEE DETAILS WHO ARE FROM INDIA OR ALSO AGE IS 20
SELECT * FROM EMP3 WHERE COUNTRY = 'INDIA' AND AGE = 20

-- GIVE EMPLOYEE TABLE WHERE NAME = 'RAVI' OR EMAIL = 'ABC@EMAIL.COM
SELECT * FROM EMP1 WHERE NAME = 'RAVI' OR EMAIL = 'ABC@EMAIL.COM'

--GIVE THE EMPLOYEE DETAILS WHERE ID IS (1,2)
SELECT * FROM EMP1 WHERE ID NOT IN (1, 2)

-- 17. AGGREGATE IN SQL
SELECT * FROM EMP1

-- 18 HOW TO FIND MAXIMUM AND MINIMUM SALARY OF EMPLOYEE FROM EMP TABLE
SELECT MAX(salary), MIN(SALARY) FROM EMP 

--19 TOTAL SALARY OF EMPLOYEE
SELECT SUM(salary) FROM EMP

--20 find the total no.of employee we have
SELECT count(salary) FROM EMP

--21 find avg salary of employee
SELECT avg(salary) FROM EMP

--group by in sql
-- we use the GROUP BY clause to group rows based on the value of columns
-- find no.of customers in each country
select * from emp

-- 22. find the no.of employee present in each country 
select count(id), address from emp group by address

-- 23. find the highest salary employee from each location
select max(salary), address from emp group by address

-- 24. find the lowest earning salary from location
select min(salary), address from emp group by address

--25. find the total salary from each location
select sum(salary), address from emp group by address

-- LIKE OPERATOR
CREATE RETAIL_DATASET(
-- THE LIKE operator is used in a WHERE clause to search for 
-- a specified pattern in a column

select * from retail_dataset

-- query 1 search all the records where description start-WHITE
SELECT * FROM retail_dataset where description LIKE "WHITE%"

-- query2 search all the records where description END -holder
SELECT * FROM retail_dataset where description LIKE '%HOLDER'

-- query3 search all the records where description is 'playhouse'
SELECT * FROM retail_dataset where description LIKE "%PLAYHOUSE%"

--QUERY 26
-- HAVING CLAUSE IN SQL

-- THE SQL HAVING clause is similar to the WHERE CLAUSE;
--ARE used to filter rows in a table based on specified criteria

-- HAVING clause was added to SQL because the WHERE keyword cannot be used with aggregate functions


-- find the address of customer where total salary is greater than 5000