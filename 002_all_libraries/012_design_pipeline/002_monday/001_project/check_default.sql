-- sql order(create new database)
create database order_new
create database employee

-- how to use specific database
use employee 

-- HOW TO DELETE DATABASE
 Drop database employee

 -- how to create table
 create table emp1(
 id INT,
 name Varchar(256) NOT NULL,
 email Varchar(256) UNIQUE,
 phone INT
 )
 SELECT * FROM EMP1
 INSERT INTO EMP1 VALUES(1, 'ABC@EMAIL.COM', 123)
 INSERT INTO EMP1 (ID,EMAIL,PHONE) VALUES(2, 'DWF@EMAIL.COM' ,234) 

 --10 CHECK AND DEFAULT CONSTRAINT

 --1. create a table emp2 where age column should only contain greater than 18.
 --2. create a table emp3 where country value automatic take INDIA as default.
 create table emp4(
 Id INT,
 AGE INT CHECK (AGE > 18),
 COUNTRY varchar(28) DEFAULT 'india'
 )
 INSERT INTO EMP4 VALUES(1, 19, 'india')
 select * from EMP4