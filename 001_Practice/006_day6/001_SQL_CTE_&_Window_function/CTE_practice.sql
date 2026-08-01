--containing employees earning more than 80000.
with eighty_k_salary AS ( select * From employees where salary > 80000)

select employee_name, salary from eighty_k_salary 

--Then return only departments whose calculated average is greater than 80000.
with dept_salary AS (select AVG(salary) as department_avg_salary, department_id from employees group by department_id)

select department_id, department_avg_salary from dept_salary where department_avg_salary > 80000.

--calculate total amount>5000 on each order by employee 
with order_totals AS( select SUM(amount) as total_amt, employee_id from Orders group by employee_id)
select total_amt, e.employee_id from order_totals o 
join employees e On o.employee_id=e.employee_id where total_amt>5000

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
