import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# =========================================================
# DATABASE CONFIG
# You can also load this connection parameters from an .ini file
# if you create one.
# =========================================================

DB_USER = "add your user"
DB_PASSWORD = "Add your password"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "edu_platform"

DATASET_PATH = Path("edu_platform_enterprise_dataset")

# =========================================================
# SQLALCHEMY ENGINE
# =========================================================

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo=False
)

# =========================================================
# FULL SCHEMA (27 TABLES)
# =========================================================

schema_sql = """

CREATE TABLE IF NOT EXISTS roles (
    role_id INT PRIMARY KEY,
    role_name VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    role_id INT,
    name VARCHAR(100),
    email VARCHAR(100),
    priority INT,
    created_at DATETIME,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100),
    duration VARCHAR(50),
    fee DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS inquiries (
    inquiry_id INT PRIMARY KEY,
    student_name VARCHAR(150),
    phone VARCHAR(20),
    status VARCHAR(50),
    course_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY,
    inquiry_id INT,
    name VARCHAR(150),
    phone VARCHAR(20),
    email VARCHAR(100),
    FOREIGN KEY (inquiry_id) REFERENCES inquiries(inquiry_id)
);

CREATE TABLE IF NOT EXISTS demo_programs (
    demo_program_id INT PRIMARY KEY,
    course_id INT,
    trainer_id INT,
    start_date DATE,
    total_days INT,
    demo_fee DECIMAL(10,2),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (trainer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS demo_enrollments (
    demo_enrollment_id INT PRIMARY KEY,
    demo_program_id INT,
    inquiry_id INT,
    FOREIGN KEY (demo_program_id) REFERENCES demo_programs(demo_program_id),
    FOREIGN KEY (inquiry_id) REFERENCES inquiries(inquiry_id)
);

CREATE TABLE IF NOT EXISTS demo_schedule (
    schedule_id INT PRIMARY KEY,
    demo_program_id INT,
    session_date DATE,
    start_time TIME,
    end_time TIME,
    FOREIGN KEY (demo_program_id) REFERENCES demo_programs(demo_program_id)
);

CREATE TABLE IF NOT EXISTS demo_attendance (
    attendance_id INT PRIMARY KEY,
    demo_enrollment_id INT,
    schedule_id INT,
    status VARCHAR(20),
    FOREIGN KEY (demo_enrollment_id) REFERENCES demo_enrollments(demo_enrollment_id),
    FOREIGN KEY (schedule_id) REFERENCES demo_schedule(schedule_id)
);

CREATE TABLE IF NOT EXISTS batches (
    batch_id INT PRIMARY KEY,
    course_id INT,
    trainer_id INT,
    mode VARCHAR(20),
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (trainer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS batch_enrollments (
    batch_enrollment_id INT PRIMARY KEY,
    batch_id INT,
    student_id INT,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS batch_schedule (
    schedule_id INT PRIMARY KEY,
    batch_id INT,
    class_date DATE,
    start_time TIME,
    end_time TIME,
    trainer_id INT,
    backup_trainer_id INT,
    status VARCHAR(50),
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
);

CREATE TABLE IF NOT EXISTS batch_attendance (
    attendance_id INT PRIMARY KEY,
    batch_enrollment_id INT,
    schedule_id INT,
    status VARCHAR(20),
    FOREIGN KEY (batch_enrollment_id) REFERENCES batch_enrollments(batch_enrollment_id),
    FOREIGN KEY (schedule_id) REFERENCES batch_schedule(schedule_id)
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id INT PRIMARY KEY,
    name VARCHAR(50),
    capacity INT
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id INT PRIMARY KEY,
    room_id INT,
    seat_number VARCHAR(20),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE IF NOT EXISTS seat_allocations (
    allocation_id INT PRIMARY KEY,
    batch_enrollment_id INT,
    seat_id INT,
    FOREIGN KEY (batch_enrollment_id) REFERENCES batch_enrollments(batch_enrollment_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
);

CREATE TABLE IF NOT EXISTS tests (
    test_id INT PRIMARY KEY,
    course_id INT,
    test_name VARCHAR(100),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE IF NOT EXISTS test_results (
    result_id INT PRIMARY KEY,
    test_id INT,
    student_id INT,
    marks INT,
    FOREIGN KEY (test_id) REFERENCES tests(test_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS mock_interviews (
    mock_id INT PRIMARY KEY,
    student_id INT,
    score INT,
    feedback TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS job_openings (
    job_id INT PRIMARY KEY,
    company_id INT,
    role VARCHAR(100),
    package DECIMAL(10,2),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id INT PRIMARY KEY,
    student_id INT,
    job_id INT,
    status VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (job_id) REFERENCES job_openings(job_id)
);

CREATE TABLE IF NOT EXISTS offers (
    offer_id INT PRIMARY KEY,
    interview_id INT,
    status VARCHAR(50),
    FOREIGN KEY (interview_id) REFERENCES interviews(interview_id)
);

CREATE TABLE IF NOT EXISTS trainer_availability (
    availability_id INT PRIMARY KEY,
    trainer_id INT,
    day_of_week VARCHAR(20),
    start_time TIME,
    end_time TIME,
    FOREIGN KEY (trainer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS trainer_leaves (
    leave_id INT PRIMARY KEY,
    trainer_id INT,
    leave_date DATE,
    FOREIGN KEY (trainer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS trainer_metrics (
    trainer_id INT PRIMARY KEY,
    total_students INT,
    avg_attendance DECIMAL(5,2),
    conversions INT,
    FOREIGN KEY (trainer_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT PRIMARY KEY,
    table_name VARCHAR(100),
    record_id INT,
    operation_type VARCHAR(20),
    old_value JSON,
    new_value JSON,
    changed_by INT
);

"""

# =========================================================
# CREATE TABLES
# =========================================================

print("Creating schema...")

with engine.begin() as conn:
    for stmt in schema_sql.split(";"):
        stmt = stmt.strip()

        if stmt:
            conn.execute(text(stmt))

print("Schema created successfully.")

# =========================================================
# TABLE LOAD ORDER
# =========================================================

load_order = [
    "roles",
    "users",
    "courses",
    "inquiries",
    "students",
    "demo_programs",
    "demo_enrollments",
    "demo_schedule",
    "demo_attendance",
    "batches",
    "batch_enrollments",
    "batch_schedule",
    "batch_attendance",
    "rooms",
    "seats",
    "seat_allocations",
    "tests",
    "test_results",
    "mock_interviews",
    "companies",
    "job_openings",
    "interviews",
    "offers",
    "trainer_availability",
    "trainer_leaves",
    "trainer_metrics",
    "audit_logs"
]

# =========================================================
# LOAD DATA
# =========================================================

for table in load_order:

    file_path = DATASET_PATH / f"{table}.csv"

    if not file_path.exists():
        print(f"[WARNING] Missing file: {file_path}")
        continue

    print(f"Loading table: {table}")

    df = pd.read_csv(file_path)

    df.to_sql(
        table,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi"
    )

    print(f"Inserted {len(df)} rows into {table}")

print("All tables loaded successfully.")

# =========================================================
# VALIDATION QUERIES
# =========================================================

validation_queries = [
    "SELECT COUNT(*) AS total_roles FROM roles",
    "SELECT COUNT(*) AS total_users FROM users",
    "SELECT COUNT(*) AS total_students FROM students",
    "SELECT COUNT(*) AS total_batches FROM batches",
    "SELECT COUNT(*) AS total_batch_enrollments FROM batch_enrollments",
    "SELECT COUNT(*) AS total_test_results FROM test_results"
]

print("\\nValidation Results:")

with engine.connect() as conn:
    for q in validation_queries:
        result = conn.execute(text(q)).fetchone()
        print(result)

print("\\nETL Completed Successfully.")
