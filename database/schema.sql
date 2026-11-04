CREATE DATABASE IF NOT EXISTS college_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE college_db;

CREATE TABLE IF NOT EXISTS admin (
    admin_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS course (
    course_id VARCHAR(20) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    dept VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS teacher (
    teacher_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    course_id VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    CONSTRAINT fk_teacher_course
        FOREIGN KEY (course_id) REFERENCES course(course_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS student (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    course_id VARCHAR(20),
    `year` INT,
    dob DATE NOT NULL,
    address VARCHAR(255),
    password VARCHAR(255) NOT NULL,
    CONSTRAINT fk_student_course
        FOREIGN KEY (course_id) REFERENCES course(course_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS subject (
    subject_id VARCHAR(20) PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    course_id VARCHAR(20),
    teacher_id VARCHAR(20),
    CONSTRAINT fk_subject_course
        FOREIGN KEY (course_id) REFERENCES course(course_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_subject_teacher
        FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    subject_id VARCHAR(20) NOT NULL,
    attendance_date DATE NOT NULL,
    `status` ENUM('Present', 'Absent') NOT NULL,
    UNIQUE KEY uq_attendance_student_subject_date
        (student_id, subject_id, attendance_date),
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_attendance_subject
        FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS marks (
    marks_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    subject_id VARCHAR(20) NOT NULL,
    marks INT NOT NULL,
    UNIQUE KEY uq_marks_student_subject (student_id, subject_id),
    CONSTRAINT chk_marks_range CHECK (marks BETWEEN 0 AND 100),
    CONSTRAINT fk_marks_student
        FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_marks_subject
        FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notice (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    date_posted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    CONSTRAINT fk_notice_admin
        FOREIGN KEY (created_by) REFERENCES admin(admin_id)
        ON DELETE SET NULL
) ENGINE=InnoDB;
