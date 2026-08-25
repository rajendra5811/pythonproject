--1.Write a SQL query to return the name and salary of employees who work in the IT department 
--and earn more than 55,000, sorted by salary from highest to lowest.
select 
       name, salary 
from  employees 
where department_name = "IT" and salary < 55000 
order by salary
--2.Write a SQL query to find customers whose total order amount is greater than 1,000.
--customer_id | total_amount (Sort by total_amount from highest to lowest.)
select 
       customer_id, SUM(order_amount) as total_amount
from customers
having total_amount > 1000
order by total_amount
group by total_amount
--3.Write a query that displays every customer, including customers who have placed no orders, along with their total order amount.
-- customer_name | total_amount (For a customer with no orders, show:)
select 
       customer_name, total_amount
from customers c
left join employees e
ON c.employee_id == e.employee_id
group by customer_name
order by total_amount
--4.Write a query that assigns a salary rank within each department, where employees with the same salary receive the same rank.
--Expected columns: name | department | salary | salary_rank
-- Assign salary rank within each department
-- Employees with same salary receive same rank
SELECT 
    name,                           
    department,                     
    salary,                         
RANK() OVER (                   
PARTITION BY department     
ORDER BY salary DESC        
    ) AS salary_rank                
FROM employees;
--5.Find employees whose salary is greater than the average salary of their own department.
--name | department | salary
WITH avg_salary AS (
    SELECT 
        department, 
        AVG(salary) AS avg_dept_salary
    FROM employees
    GROUP BY department
)
SELECT 
    e.name, 
    e.department, 
    e.salary
FROM employees e
JOIN avg_salary a ON e.department = a.department
WHERE e.salary > a.avg_dept_salary;


