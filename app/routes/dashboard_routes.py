from datetime import date

from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import mysql
from . import route


@route('/dashboard')
@login_required
def dashboard():
    stats = {}
    if current_user.role == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as count FROM student"); stats['total_students'] = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM teacher"); stats['total_teachers'] = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM course"); stats['total_courses'] = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM subject"); stats['total_subjects'] = cur.fetchone()['count']

        cur.execute("SELECT c.course_name, COUNT(s.student_id) as count FROM course c LEFT JOIN student s ON c.course_id = s.course_id GROUP BY c.course_name")
        student_data = cur.fetchall()
        stats['course_labels'] = [row['course_name'] for row in student_data]
        stats['course_data'] = [row['count'] for row in student_data]

        cur.execute("SELECT c.course_name, COUNT(t.teacher_id) as count FROM course c LEFT JOIN teacher t ON c.course_id = t.course_id GROUP BY c.course_name")
        faculty_data = cur.fetchall()
        stats['faculty_labels'] = [row['course_name'] for row in faculty_data]
        stats['faculty_data'] = [row['count'] for row in faculty_data]

        cur.execute("SELECT c.course_name, COUNT(s.subject_id) as count FROM course c LEFT JOIN subject s ON c.course_id = s.course_id GROUP BY c.course_name")
        subject_data = cur.fetchall()
        stats['subject_labels'] = [row['course_name'] for row in subject_data]
        stats['subject_data'] = [row['count'] for row in subject_data]
        cur.close()
        return render_template('admin_dashboard.html', stats=stats)

    elif current_user.role == 'teacher':
        cur = mysql.connection.cursor()
        cur.execute("SELECT t.*, s.subject_name, s.subject_id, c.course_name FROM teacher t LEFT JOIN subject s ON t.teacher_id = s.teacher_id LEFT JOIN course c ON t.course_id = c.course_id WHERE t.teacher_id = %s", (current_user.id,))
        teacher_data = cur.fetchone() or {}
        if teacher_data.get('subject_id'):
            sub_id = teacher_data['subject_id']
            cur.execute("SELECT status, COUNT(*) as count FROM attendance WHERE subject_id = %s AND attendance_date = %s GROUP BY status", (sub_id, date.today()))
            att_data = cur.fetchall()
            present = next((r['count'] for r in att_data if r['status']=='Present'), 0)
            absent = next((r['count'] for r in att_data if r['status']=='Absent'), 0)
            stats['att_labels'] = ['Present', 'Absent']; stats['att_data'] = [present, absent]
            cur.execute("SELECT marks FROM marks WHERE subject_id = %s", (sub_id,))
            marks = [m['marks'] for m in cur.fetchall()]
            grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
            for m in marks:
                if m >= 80: grades['A'] += 1
                elif m >= 60: grades['B'] += 1
                elif m >= 50: grades['C'] += 1
                elif m >= 40: grades['D'] += 1
                else: grades['F'] += 1
            stats['grade_labels'] = list(grades.keys()); stats['grade_data'] = list(grades.values())
        else:
            stats['att_labels'] = []; stats['att_data'] = []
            stats['grade_labels'] = []; stats['grade_data'] = []
        cur.close()
        return render_template('teacher_dashboard.html', teacher_data=teacher_data, stats=stats)

    elif current_user.role == 'student':
        cur = mysql.connection.cursor()
        cur.execute("SELECT s.*, c.course_name FROM student s LEFT JOIN course c ON s.course_id = c.course_id WHERE s.student_id = %s", (current_user.id,))
        student_data = cur.fetchone()
        cur.execute("SELECT COUNT(*) as count FROM attendance WHERE student_id = %s", (current_user.id,))
        total_days = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) as count FROM attendance WHERE student_id = %s AND status = 'Present'", (current_user.id,))
        present_days = cur.fetchone()['count']
        cur.execute("SELECT m.marks, s.subject_name FROM marks m JOIN subject s ON m.subject_id = s.subject_id WHERE m.student_id = %s", (current_user.id,))
        marks_recs = cur.fetchall()
        cur.close()
        attendance_data = {'present': present_days, 'absent': total_days - present_days, 'total': total_days}
        stats['marks_labels'] = [m['subject_name'] for m in marks_recs]
        stats['marks_values'] = [m['marks'] for m in marks_recs]
        return render_template('student_dashboard.html', student_data=student_data, attendance_data=attendance_data, marks_data=marks_recs, stats=stats)
    return redirect(url_for('login'))
