from datetime import date

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import mysql
from ..forms import AttendanceForm, MarksForm
from . import route


@route('/teacher/attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'teacher': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subject WHERE teacher_id = %s", (current_user.id,))
    subject = cur.fetchone()
    if not subject: flash('No subject assigned.', 'danger'); cur.close(); return redirect(url_for('dashboard'))
    today = date.today().isoformat()
    cur.execute("SELECT student_id, name FROM student WHERE course_id = %s", (subject['course_id'],))
    students = cur.fetchall()
    cur.execute("SELECT student_id, status FROM attendance WHERE subject_id = %s AND attendance_date = %s", (subject['subject_id'], today))
    existing = {row['student_id']: row['status'] for row in cur.fetchall()}
    cur.close()
    student_data = [{'user_id': s['student_id'], 'name': s['name'], 'status': existing.get(s['student_id'], 'Present')} for s in students]
    form = AttendanceForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            for subform in form.students:
                cur.execute("INSERT INTO attendance (student_id, subject_id, attendance_date, status) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE status=%s", (subform.student_id.data, subject['subject_id'], today, subform.status.data, subform.status.data))
            mysql.connection.commit(); flash('Saved!', 'success')
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
        return redirect(url_for('mark_attendance'))
    if request.method == 'GET':
        for s in student_data: form.students.append_entry({'student_id': s['user_id'], 'status': s['status']})
    return render_template('mark_attendance.html', form=form, students=student_data, subject=subject, today=today)

@route('/teacher/marks', methods=['GET', 'POST'])
@login_required
def add_marks():
    if current_user.role != 'teacher': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subject WHERE teacher_id = %s", (current_user.id,))
    subject = cur.fetchone()
    if not subject: flash('No subject assigned.', 'danger'); cur.close(); return redirect(url_for('dashboard'))
    cur.execute("SELECT s.student_id, s.name, m.marks FROM student s LEFT JOIN marks m ON s.student_id = m.student_id AND m.subject_id = %s WHERE s.course_id = %s", (subject['subject_id'], subject['course_id']))
    students = cur.fetchall(); cur.close()
    student_data = [{'user_id': s['student_id'], 'name': s['name'], 'marks': s.get('marks')} for s in students]
    form = MarksForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            for subform in form.students:
                if subform.marks.data is not None:
                    cur.execute("INSERT INTO marks (student_id, subject_id, marks) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE marks=%s", (subform.student_id.data, subject['subject_id'], subform.marks.data, subform.marks.data))
            mysql.connection.commit(); flash('Saved!', 'success')
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
        return redirect(url_for('add_marks'))
    if request.method == 'GET':
        for s in student_data: form.students.append_entry({'student_id': s['user_id'], 'marks': s['marks']})
    return render_template('add_marks.html', form=form, students=student_data, subject=subject)

@route('/teacher/students')
@login_required
def view_my_students():
    if current_user.role != 'teacher': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT subject_id, course_id FROM subject WHERE teacher_id = %s", (current_user.id,))
    subject = cur.fetchone()
    if not subject: flash('No subject assigned.', 'warning'); cur.close(); return redirect(url_for('dashboard'))
    cur.execute("SELECT student_id, name, email FROM student WHERE course_id = %s", (subject['course_id'],))
    students = cur.fetchall()
    student_data = []
    for s in students:
        cur.execute("SELECT COUNT(*) as total FROM attendance WHERE student_id = %s AND subject_id = %s", (s['student_id'], subject['subject_id']))
        total = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as present FROM attendance WHERE student_id = %s AND subject_id = %s AND status = 'Present'", (s['student_id'], subject['subject_id']))
        present = cur.fetchone()['present']
        att_percent = (present / total * 100) if total > 0 else 0
        cur.execute("SELECT marks FROM marks WHERE student_id = %s AND subject_id = %s", (s['student_id'], subject['subject_id']))
        marks = cur.fetchone(); marks = marks['marks'] if marks else 'N/A'
        student_data.append({'student_id': s['student_id'], 'name': s['name'], 'email': s['email'], 'attendance': round(att_percent,1), 'marks': marks})
    cur.close()
    return render_template('teacher_view_students.html', students=student_data)

@route('/student/attendance')
@login_required
def view_attendance():
    if current_user.role != 'student': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT a.attendance_date, a.status, s.subject_id, s.subject_name FROM attendance a JOIN subject s ON a.subject_id = s.subject_id WHERE a.student_id = %s ORDER BY s.subject_name, a.attendance_date DESC", (current_user.id,))
    records = cur.fetchall(); cur.close()
    attendance_by_subject = {}
    for r in records:
        sub_id = r['subject_id']
        if sub_id not in attendance_by_subject: attendance_by_subject[sub_id] = {'subject_name': r['subject_name'], 'present': 0, 'total': 0, 'records': []}
        attendance_by_subject[sub_id]['records'].append(r)
        attendance_by_subject[sub_id]['total'] += 1
        if r['status'] == 'Present': attendance_by_subject[sub_id]['present'] += 1
    final_list = []
    for sub_id, data in attendance_by_subject.items():
        data['percentage'] = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0; data['subject_id'] = sub_id; final_list.append(data)
    return render_template('view_attendance.html', attendance_by_subject=final_list)

@route('/student/results')
@login_required
def view_results():
    if current_user.role != 'student': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.course_name FROM student s JOIN course c ON s.course_id = c.course_id WHERE s.student_id = %s", (current_user.id,))
    course = cur.fetchone()
    cur.execute("SELECT m.marks, s.subject_id, s.subject_name FROM marks m JOIN subject s ON m.subject_id = s.subject_id WHERE m.student_id = %s", (current_user.id,))
    marks_list = cur.fetchall(); cur.close()
    results_data = {'course_name': course['course_name'] if course else 'N/A', 'results': [], 'total_marks': 0, 'max_marks': 0, 'overall_percentage': 0, 'overall_grade': 'N/A'}
    if not marks_list: return render_template('view_results.html', results_data=None)
    total_marks = 0; num_subjects = len(marks_list)
    for item in marks_list:
        marks = item.get('marks'); grade = 'F'
        if marks:
            if marks >= 90: grade = 'A+'
            elif marks >= 80: grade = 'A'
            elif marks >= 70: grade = 'B+'
            elif marks >= 60: grade = 'B'
            elif marks >= 50: grade = 'C'
            elif marks >= 40: grade = 'D'
            total_marks += marks
        results_data['results'].append({'subject_name': item['subject_name'], 'marks': marks or 'N/A', 'grade': grade, 'status': 'Pass' if grade != 'F' else 'Fail'})
    results_data['total_marks'] = total_marks; results_data['max_marks'] = num_subjects * 100
    results_data['overall_percentage'] = (total_marks / (num_subjects * 100)) * 100 if num_subjects > 0 else 0
    p = results_data['overall_percentage']
    if p >= 90: results_data['overall_grade'] = 'A+'
    elif p >= 80: results_data['overall_grade'] = 'A'
    elif p >= 70: results_data['overall_grade'] = 'B+'
    elif p >= 60: results_data['overall_grade'] = 'B'
    elif p >= 50: results_data['overall_grade'] = 'C'
    elif p >= 40: results_data['overall_grade'] = 'D'
    else: results_data['overall_grade'] = 'F'
    return render_template('view_results.html', results_data=results_data)
