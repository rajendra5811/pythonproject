--Q1 — Aggregation 🟢 5/10 easy
--Find the average, minimum, and maximum salary for each department.
--Return: department_id | avg_salary | min_salary | max_salary
select AVG(e.salary)as avg_salary , MIN(e.salary)as min_salary, MAX(e.salary) as max_salary, e.department_id, e.department_name from employees e 
join departments d ON e.department_id = d.department_id Group By department_id

--Q2 — JOIN 🟢 5/10 easy
--Display every employee and their department name.
--Employees without a department must also appear.
--Return:employee_name | department_name
--Think carefully about which JOIN preserves all employees.
select d.department_name, e.employee_name from employees e 
left join departments d ON e.department_id = d.department_id where e.deparment_id IS Null

--Q3 — GROUP BY + HAVING 🟡 6/10 medium
--Find employees who handled orders with a total order amount greater than 5000.
--Return:employee_id | total_amount, Do not use a subquery.
select SUM(o.amount), e.employee_name from employees e 
join o.orders ON e.employee_id = o.employee_id having o.amount > 5000 group by employee_id Order By amount Desc 

--Q4 — Subquery 🟡 6/10 medium
--Find employees whose salary is greater than the overall company average salary.
--Return:employee_name | salary, Requirement: use a subquery.
select  salary, employee_name, AVG(salary) as avg_salary from (select * from employees having salary > avg_salary) order by salary DESC 
SELECT
    e.employee_name,
    d.department_name,
    e.salary,
    dept_avg.department_average
FROM employees e
JOIN departments d
ON e.department_id = d.department_id
JOIN (
    SELECT
        department_id,
        AVG(salary) AS department_average
    FROM employees
    GROUP BY department_id
) dept_avg
ON e.department_id = dept_avg.department_id
WHERE e.salary > dept_avg.department_average;
--Q5 — Data Cleansing 🟠 7/10 moderate
--The database contains names such as:"  RAJ  ","raj","Raj","priya","PRIYA "
--Produce:Raj, Priya
--Requirements: Remove spaces.Standardize case.Remove duplicates.
SELECT DISTINCT
    INITCAP(TRIM(LOWER(employee_name))) AS employee_name
FROM employees;

--Q6 — CTE + JOIN 🟠 7/10 moderate
--Using a CTE, calculate the total order amount handled by each employee.
--Then display only employees whose total order amount is greater than 4000.
--Return: employee_name | department_name | total_order_amount
--This requires:Orders → CTE → Employees → Departments
with amount_table(select SUM(o.amount) as total amount, e.employee_name from employees e 
join o.orders ON e.employee_id = o.employee_id ) 
select e.employee_name, d.department_name, total_order_amount from amount_table having o.amount > 4000 group by employee_id Order By amount Desc
--Q7 — Window Functions 🔴 8/10 hard
--Rank employees by salary inside their department.
--Return:employee_name,department_id,salary, salary_rank,department_avg_salary
--Requirements: Use two window functions:DENSE_RANK(),AVG(), OVER(),Do not use GROUP BY.
WITH RankedSalaries AS (
    SELECT 
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) as salary_rank
    FROM employees
)
SELECT DISTINCT salary , employee_name,department_id, salary_rank
FROM RankedSalaries ,

--Q8 — Advanced SQL 🔴 9/10 hard
--Find the second-highest-paid employee in each department.
--Return:employee_name,department_name,salary,salary_rank
--Important: two employees can have the same salary.
--Use:CTE,JOIN,DENSE_RANK(),PARTITION BY
WITH RankedSalaries AS (
    SELECT 
        salary,
        DENSE_RANK() OVER (ORDER BY salary DESC) as rnk
    FROM employees e join departments d on e.department_id = d.department_id
)
SELECT DISTINCT salary 
FROM RankedSalaries 
WHERE rnk = 2;
