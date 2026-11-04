from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import mysql
from ..forms import CourseForm, NoticeForm, StudentForm, SubjectForm, TeacherForm, UploadFileForm
from ..services import create_password_hash, process_import
from . import route


@route('/admin/students')
@login_required
def view_students():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT s.*, c.course_name FROM student s LEFT JOIN course c ON s.course_id = c.course_id"); students = cur.fetchall(); cur.close()
    return render_template('view_students.html', students=students)

@route('/admin/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = StudentForm()
    cur = mysql.connection.cursor(); cur.execute("SELECT course_id, course_name FROM course"); courses = cur.fetchall(); cur.close()
    form.course_id.choices = [("", "Select Course")] + [(c['course_id'], c['course_name']) for c in courses]
    if form.validate_on_submit():
        hashed = create_password_hash()
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO student (student_id, name, email, dob, course_id, password) VALUES (%s,%s,%s,%s,%s,%s)", (form.student_id.data, form.name.data, form.email.data, form.dob.data, form.course_id.data, hashed))
            mysql.connection.commit(); flash('Student added!', 'success'); return redirect(url_for('view_students'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_student.html', form=form, is_edit_mode=False)

@route('/admin/students/import', methods=['GET', 'POST'])
@login_required
def import_students():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = UploadFileForm()
    if form.validate_on_submit():
        success, errors = process_import(form.file.data, 'student')
        flash(f'Imported {success} students.', 'success' if success > 0 else 'warning')
        for error in errors[:5]:
            flash(error, 'danger')
        return redirect(url_for('view_students'))
    return render_template('import_data.html', form=form, type='Students')

@route('/admin/students/edit/<string:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM student WHERE student_id = %s", (student_id,)); student = cur.fetchone(); cur.close()
    if not student: flash('Not found', 'danger'); return redirect(url_for('view_students'))
    form = StudentForm(obj=student)
    cur = mysql.connection.cursor(); cur.execute("SELECT course_id, course_name FROM course"); courses = cur.fetchall(); cur.close()
    form.course_id.choices = [("", "Select Course")] + [(c['course_id'], c['course_name']) for c in courses]
    if request.method == 'GET': form.course_id.data = student['course_id']; form.dob.data = student['dob']
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE student SET name=%s, email=%s, dob=%s, course_id=%s WHERE student_id=%s", (form.name.data, form.email.data, form.dob.data, form.course_id.data, student_id))
            mysql.connection.commit(); flash('Updated!', 'success'); return redirect(url_for('view_students'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_student.html', form=form, is_edit_mode=True)

@route('/admin/students/delete/<string:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM marks WHERE student_id=%s", (student_id,))
        cur.execute("DELETE FROM attendance WHERE student_id=%s", (student_id,))
        cur.execute("DELETE FROM student WHERE student_id=%s", (student_id,))
        mysql.connection.commit(); flash('Deleted!', 'success')
    except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
    finally: cur.close()
    return redirect(url_for('view_students'))

@route('/admin/teachers')
@login_required
def view_teachers():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT t.*, c.course_name FROM teacher t LEFT JOIN course c ON t.course_id = c.course_id"); teachers = cur.fetchall(); cur.close()
    return render_template('view_teachers.html', teachers=teachers)

@route('/admin/teachers/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = TeacherForm()
    cur = mysql.connection.cursor(); cur.execute("SELECT course_id, course_name FROM course"); courses = cur.fetchall(); cur.close()
    form.course_id.choices = [("", "Select Dept")] + [(c['course_id'], c['course_name']) for c in courses]
    if form.validate_on_submit():
        hashed = create_password_hash()
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO teacher (teacher_id, name, email, course_id, password) VALUES (%s,%s,%s,%s,%s)", (form.teacher_id.data, form.name.data, form.email.data, form.course_id.data, hashed))
            mysql.connection.commit(); flash('Teacher added!', 'success'); return redirect(url_for('view_teachers'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_teacher.html', form=form, is_edit_mode=False)

@route('/admin/teachers/import', methods=['GET', 'POST'])
@login_required
def import_teachers():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = UploadFileForm()
    if form.validate_on_submit():
        success, errors = process_import(form.file.data, 'teacher')
        flash(f'Imported {success} teachers.', 'success' if success > 0 else 'warning')
        for error in errors[:5]:
            flash(error, 'danger')
        return redirect(url_for('view_teachers'))
    return render_template('import_data.html', form=form, type='Faculty')

@route('/admin/teachers/edit/<string:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM teacher WHERE teacher_id = %s", (teacher_id,)); teacher = cur.fetchone(); cur.close()
    if not teacher: flash('Not found', 'danger'); return redirect(url_for('view_teachers'))
    form = TeacherForm(obj=teacher)
    cur = mysql.connection.cursor(); cur.execute("SELECT course_id, course_name FROM course"); courses = cur.fetchall(); cur.close()
    form.course_id.choices = [("", "Select Dept")] + [(c['course_id'], c['course_name']) for c in courses]
    if request.method == 'GET': form.course_id.data = teacher['course_id']
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE teacher SET name=%s, email=%s, course_id=%s WHERE teacher_id=%s", (form.name.data, form.email.data, form.course_id.data, teacher_id))
            mysql.connection.commit(); flash('Updated!', 'success'); return redirect(url_for('view_teachers'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_teacher.html', form=form, is_edit_mode=True)

@route('/admin/teachers/delete/<string:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE subject SET teacher_id = NULL WHERE teacher_id = %s", (teacher_id,))
        cur.execute("DELETE FROM teacher WHERE teacher_id = %s", (teacher_id,))
        mysql.connection.commit(); flash('Deleted!', 'success')
    except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
    finally: cur.close()
    return redirect(url_for('view_teachers'))

@route('/admin/courses')
@login_required
def view_courses():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM course"); courses = cur.fetchall(); cur.close()
    return render_template('view_courses.html', courses=courses)

@route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = CourseForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO course (course_id, course_name) VALUES (%s, %s)", (form.course_id.data, form.course_name.data))
            mysql.connection.commit(); flash('Course added!', 'success'); return redirect(url_for('view_courses'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_course.html', form=form, is_edit_mode=False)

@route('/admin/courses/import', methods=['GET', 'POST'])
@login_required
def import_courses():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = UploadFileForm()
    if form.validate_on_submit():
        success, errors = process_import(form.file.data, 'course')
        flash(f'Imported {success} courses.', 'success' if success > 0 else 'warning')
        for error in errors[:5]:
            flash(error, 'danger')
        return redirect(url_for('view_courses'))
    return render_template('import_data.html', form=form, type='Courses')

@route('/admin/courses/edit/<string:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM course WHERE course_id = %s", (course_id,)); course = cur.fetchone(); cur.close()
    if not course: flash('Not found', 'danger'); return redirect(url_for('view_courses'))
    form = CourseForm(obj=course); form.course_id.render_kw = {'readonly': True}
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE course SET course_name=%s WHERE course_id=%s", (form.course_name.data, course_id))
            mysql.connection.commit(); flash('Updated!', 'success'); return redirect(url_for('view_courses'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_course.html', form=form, is_edit_mode=True)

@route('/admin/courses/delete/<string:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM subject WHERE course_id=%s", (course_id,))
        cur.execute("DELETE FROM course WHERE course_id=%s", (course_id,))
        mysql.connection.commit(); flash('Deleted!', 'success')
    except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
    finally: cur.close()
    return redirect(url_for('view_courses'))

@route('/admin/subjects')
@login_required
def view_subjects():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT s.*, c.course_name, t.name as teacher_name FROM subject s LEFT JOIN course c ON s.course_id=c.course_id LEFT JOIN teacher t ON s.teacher_id=t.teacher_id"); subjects = cur.fetchall(); cur.close()
    return render_template('view_subjects.html', subjects=subjects)

@route('/admin/subjects/add', methods=['GET', 'POST'])
@login_required
def add_subject():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = SubjectForm()
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_id, course_name FROM course"); courses = cur.fetchall()
    cur.execute("SELECT teacher_id, name FROM teacher"); teachers = cur.fetchall(); cur.close()
    form.course_id.choices = [("", "Select Course")] + [(c['course_id'], c['course_name']) for c in courses]
    form.teacher_id.choices = [("", "Select Teacher")] + [(t['teacher_id'], t['name']) for t in teachers]
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO subject (subject_id, subject_name, course_id, teacher_id) VALUES (%s,%s,%s,%s)", (form.subject_id.data, form.subject_name.data, form.course_id.data, form.teacher_id.data))
            mysql.connection.commit(); flash('Subject added!', 'success'); return redirect(url_for('view_subjects'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_subject.html', form=form, is_edit_mode=False)

@route('/admin/subjects/import', methods=['GET', 'POST'])
@login_required
def import_subjects():
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    form = UploadFileForm()
    if form.validate_on_submit():
        success, errors = process_import(form.file.data, 'subject')
        flash(f'Imported {success} subjects.', 'success' if success > 0 else 'warning')
        for error in errors[:5]:
            flash(error, 'danger')
        return redirect(url_for('view_subjects'))
    return render_template('import_data.html', form=form, type='Subjects')

@route('/admin/subjects/edit/<string:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM subject WHERE subject_id = %s", (subject_id,)); subject = cur.fetchone(); cur.close()
    if not subject: flash('Not found', 'danger'); return redirect(url_for('view_subjects'))
    form = SubjectForm(obj=subject); form.subject_id.render_kw = {'readonly': True}
    cur = mysql.connection.cursor()
    cur.execute("SELECT course_id, course_name FROM course"); courses = cur.fetchall()
    cur.execute("SELECT teacher_id, name FROM teacher"); teachers = cur.fetchall(); cur.close()
    form.course_id.choices = [("", "Select Course")] + [(c['course_id'], c['course_name']) for c in courses]
    form.teacher_id.choices = [("", "Select Teacher")] + [(t['teacher_id'], t['name']) for t in teachers]
    if request.method == 'GET': form.course_id.data = subject['course_id']; form.teacher_id.data = subject['teacher_id']
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE subject SET subject_name=%s, course_id=%s, teacher_id=%s WHERE subject_id=%s", (form.subject_name.data, form.course_id.data, form.teacher_id.data, subject_id))
            mysql.connection.commit(); flash('Updated!', 'success'); return redirect(url_for('view_subjects'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_subject.html', form=form, is_edit_mode=True)

@route('/admin/subjects/delete/<string:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin': return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM marks WHERE subject_id=%s", (subject_id,))
        cur.execute("DELETE FROM attendance WHERE subject_id=%s", (subject_id,))
        cur.execute("DELETE FROM subject WHERE subject_id=%s", (subject_id,))
        mysql.connection.commit(); flash('Deleted!', 'success')
    except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
    finally: cur.close()
    return redirect(url_for('view_subjects'))

@route('/admin/notices')
@login_required
def view_notices():
    cur = mysql.connection.cursor(); cur.execute("SELECT * FROM notice ORDER BY date_posted DESC"); notices = cur.fetchall(); cur.close()
    return render_template('view_notices.html', notices=notices)

@route('/admin/notices/add', methods=['GET', 'POST'])
@login_required
def add_notice():
    if current_user.role != 'admin': return redirect(url_for('view_notices'))
    form = NoticeForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO notice (title, content, created_by) VALUES (%s,%s,%s)", (form.title.data, form.content.data, current_user.id))
            mysql.connection.commit(); flash('Posted!', 'success'); return redirect(url_for('view_notices'))
        except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
        finally: cur.close()
    return render_template('add_notice.html', form=form)

@route('/admin/notices/delete/<int:notice_id>', methods=['POST'])
@login_required
def delete_notice(notice_id):
    if current_user.role != 'admin': return redirect(url_for('view_notices'))
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM notice WHERE notice_id = %s", (notice_id,))
        mysql.connection.commit(); flash('Deleted!', 'success')
    except Exception as e: mysql.connection.rollback(); flash(f'Error: {e}', 'danger')
    finally: cur.close()
    return redirect(url_for('view_notices'))
