--- TOP/LIMIT 

--1.QUERY: HOW TO GET ONLY FIRST 3 RECORD FROM TABLE
SELECT TOP 3 * FROM EMPLOYEE
SELECT * FROM EMPLOYEE LIMIT 3

--2. QUERY HOW TO GET 50% RECORDS FROM TABLE
select TOP 50 PERCENT * FROM EMPLOYEE

--3. WRITE QUERY TO GET TOP 2 HIGHEST SALARY OF EMPLOYEE
SELECT TOP 2 * FROM EMPLOYEE ORDER BY SALARY DESC

--4.WRITE QUERY TO GET BOTTOM 2 SALARY OF EMPLOYEE
SELECT TOP 2 * FROM EMPLOYEE ORDER BY SALARY ASC

--5: QUERY TO GET TOP 2 RECORDS FROM INDIA BASED ON SALARY
SELECT top 2 * FROM EMPLOYEE WHERE LOCATION = 'india' order by salary desc

--Unique records(distinct)
select * from employees

select distinct name, id, salary, location, dept from employees

-- COALESCE IN SQL
select * from employees

--Replace NULL Phone Numbers with unknown
SELECT NAME, COALESCE(PHONE, 'Unknown') from employees 

--Select the First Available Email:(first not null values)
select name, coalesce(email, alternate_email, 'Unknown') from employees

--Calculate Total Compensation(Salary + Bonous):
select salary + coalesce(bonus, 0) from employees