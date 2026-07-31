--1.find total salary for each department
SELECT
    department_id,
    SUM(salary) AS total_salary
FROM employees
GROUP BY department_id;
--Find departments with at least 5 employees whose average salary exceeds 70,000.
SELECT
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
HAVING COUNT(*) >= 5
   AND AVG(salary) > 70000;
--Find the number of employees in each department.
select 
      count(*)as employee_count,
	  department_id 
from employees
Group by department_id
--Find departments whose average salary is greater than 80000.
select 
      department_id,
	  AVG(salary) as avg_salary 
from employees 
group by department_id 
having AVG(salary) >8000
--Using orders, find employees who handled at least 3 orders AND more than 5000 total order amount.
select 
        SUM(amount) as total_amount,
		Count(order_id) as count_orders, 
		employee_id 
from Orders 
group by employee_id 
having Count(order_id) >2 AND sum(amount) > 5000
--Only employees having a valid department should appear.
select 
       e.employee_name, 
	   d.department_name 
 from employees e 
Join departments d 
On d.department_id = e.department_id
--Every employee must appear, including employees without departments.
select 
       e.employee_name, 
	   d.department_name 
from employees e 
Left Join departments d 
On d.department_id = e.department_id 
--Find customers who have never placed an order.
select 
        c.customer_id, 
		c.customer_name 
from orders o 
right join customers c 
On o.customer_id = c.customer_id 
where order_id is Null
--Find employees earning more than the company average.
SELECT
    employee_name,
    salary
FROM employees
WHERE salary >
(
    SELECT AVG(salary)
    FROM employees
);
--Find employees earning more than the company average salary.
select
       employee_name,
	   department_id,
	   salary
from employees where salary >
(        select 
               AVG(salary) 
		 from employees 
		 )
--Find employees earning the maximum salary in the company.Notice there is no GROUP BY required.
select 
       employee_name,
	   salary
From employees 
where salary = (select MAX(salary) from employees)

--Find employees earning more than the average salary of their own department.Order by department_id
select 
       e.employee_name, 
	   e.salary 
from employees e
where salary > (
                select 
				       AVG(e2.salary) 
				from employees e2
				where e2.department_id = e.department_id
)
Order By e.department_id