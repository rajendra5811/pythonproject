--1.Find the total salary paid by each department.
select sum(salary) as total_salary, department_id from employees group by department_id.

--2.Find departments with: at least 5 employees average salary greater than 80000 Return:
select 
       count(employee_id) as count_of_employee,
	   department_id, 
	   AVG(salary) as average_salary
from employees group by department_id
	   having count(employee_id) >= 5 and AVG(salary) > 80000
--3.Find employees who handled more than 3 orders.
select 
             employee_id,
             count(order_id) as order_count,
             Sum(amount) as total_amount
from Orders group by emmployee_id having count(order_id) > 3
--4.Find the city having the highest average salary.
select 
           max(avg(salary)) as highest_avg_salary, 
		   city
from employees group by city

select 
         max(avg_salary) as max_avg_salary,
		 city
from (select avg(salary) as avg_salary from employees group by city)
          




--department avg salary but Employees disappeared.
SELECT
    department_id,
    AVG(salary)
FROM employees
GROUP BY department_id;
-- window fuction avg_department_salary but Employees remain.
SELECT
    employee_name,
    department_id,
    salary,
    AVG(salary) OVER
    (
        PARTITION BY department_id
    ) AS department_average

FROM employees;
--Top salary in each department.
SELECT

employee_name,

department_id,

salary,

DENSE_RANK()

OVER(

PARTITION BY department_id

ORDER BY salary DESC

)

FROM employees;
