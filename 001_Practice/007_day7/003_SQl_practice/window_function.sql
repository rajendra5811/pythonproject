
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
