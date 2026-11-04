import pandas as pd
from flask import current_app
from werkzeug.security import generate_password_hash

from .extensions import mysql


IMPORTS = {
    "student": (
        ("student_id", "name", "email", "dob", "course_id"),
        "INSERT INTO student (student_id, name, email, dob, course_id, password) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
    ),
    "teacher": (
        ("teacher_id", "name", "email", "course_id"),
        "INSERT INTO teacher (teacher_id, name, email, course_id, password) "
        "VALUES (%s, %s, %s, %s, %s)",
    ),
    "course": (
        ("course_id", "course_name"),
        "INSERT INTO course (course_id, course_name) VALUES (%s, %s)",
    ),
    "subject": (
        ("subject_id", "subject_name", "course_id", "teacher_id"),
        "INSERT INTO subject (subject_id, subject_name, course_id, teacher_id) "
        "VALUES (%s, %s, %s, %s)",
    ),
}


def create_password_hash():
    return generate_password_hash(current_app.config["INITIAL_USER_PASSWORD"])


def process_import(file, record_type):
    if record_type not in IMPORTS:
        raise ValueError(f"Unsupported import type: {record_type}")

    required_columns, query = IMPORTS[record_type]
    data = pd.read_excel(file)
    data.columns = [str(column).strip() for column in data.columns]
    missing_columns = set(required_columns).difference(data.columns)
    if missing_columns:
        return 0, [f"Missing required columns: {', '.join(sorted(missing_columns))}"]

    cursor = mysql.connection.cursor()
    success_count = 0
    errors = []
    password_hash = create_password_hash()
    try:
        for index, row in data.iterrows():
            try:
                values = [row[column] for column in required_columns]
                if record_type in ("student", "teacher"):
                    values.append(password_hash)
                cursor.execute(query, tuple(values))
                success_count += 1
            except Exception as error:
                errors.append(f"Row {index + 2}: {error}")
        mysql.connection.commit()
    except Exception:
        mysql.connection.rollback()
        raise
    finally:
        cursor.close()

    return success_count, errors
