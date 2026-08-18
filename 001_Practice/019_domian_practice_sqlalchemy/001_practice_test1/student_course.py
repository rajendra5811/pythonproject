# PART A — SQLAlchemy Core Retrieval
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy import insert, select, update, delete

# Engine
engine = create_engine('sqlite:///example.db', echo=True)
meta = MetaData()

# ---------------------------
# Table definitions
# ---------------------------

students = Table(
    "students", meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("age", Integer, nullable=True),
    Column("department", String(50), nullable=True)
)

courses = Table(
    "courses", meta,
    Column("id", Integer, primary_key=True),
    Column("course_name", String(50), nullable=False),
    Column("credits", Integer, nullable=True)
)

# Enrollments with composite primary key (student_id, course_id)
enrollments = Table(
    "enrollments", meta,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("grade", String(2), nullable=True)
)

# Create all tables
meta.create_all(engine)

# ---------------------------
# 1. INSERT — Insert 3 students
# ---------------------------
with engine.connect() as conn:
    stmt = insert(students).values([
        {"name": "Alice", "age": 20, "department": "science"},
        {"name": "Bob",   "age": 22, "department": "arts"},
        {"name": "Carol", "age": 21, "department": "science"},
    ])
    result = conn.execute(stmt)
    conn.commit()
    print("Inserted students, ids:", result.inserted_primary_key_rows)

# ---------------------------
# 2. SELECT — Find students from "science"
# ---------------------------
with engine.connect() as conn:
    stmt = select(students).where(students.c.department == "science")
    result = conn.execute(stmt)
    for row in result:
        print("Science student:", row.id, row.name, row.department)

# ---------------------------
# 3. UPDATE — Change one student's department
# ---------------------------
with engine.connect() as conn:
    stmt = (
        update(students)
        .where(students.c.name == "Bob")
        .values(department="science")
    )
    result = conn.execute(stmt)
    conn.commit()
    print("Rows updated:", result.rowcount)

# ---------------------------
# 4. DELETE — Delete one student
# ---------------------------
with engine.connect() as conn:
    # First, delete any enrollments for that student (to avoid FK issues)
    stmt_del_enroll = delete(enrollments).where(enrollments.c.student_id == 2)
    conn.execute(stmt_del_enroll)

    # Then delete the student
    stmt_del_student = delete(students).where(students.c.id == 2)
    result = conn.execute(stmt_del_student)
    conn.commit()
    print("Rows deleted:", result.rowcount)

# ---------------------------
# 5. JOIN — Join students and enrollments
# ---------------------------
with engine.connect() as conn:
    stmt = (
        select(students.c.name, enrollments.c.course_id, enrollments.c.grade)
        .select_from(
            students.join(
                enrollments,
                students.c.id == enrollments.c.student_id
            )
        )
    )
    result = conn.execute(stmt)
    for row in result:
        print("Enrollment:", row.name, row.course_id, row.grade)

# ---------------------------
# 6. TRANSACTION — Perform an operation and commit
# ---------------------------
with engine.connect() as conn:
    # Start an implicit transaction
    stmt = insert(students).values(name="Dave", age=23, department="commerce")
    result = conn.execute(stmt)
    # If you do NOT call conn.commit(), the INSERT is rolled back when the block ends.
    conn.commit()
    print("Committed new student, id:", result.inserted_primary_key)

# ---------------------------
# What happens if you don't commit?
# ---------------------------
# In SQLAlchemy Core, when you use engine.connect() and execute write operations
# (INSERT/UPDATE/DELETE), those changes are part of a transaction.
#
# - If you call conn.commit(), the transaction is committed and changes are saved.
# - If you do NOT call conn.commit(), the transaction is rolled back when the
#   connection context exits, so the changes are lost.
#
# This protects data integrity: accidental errors or uncommitted work do not
# permanently modify the database.