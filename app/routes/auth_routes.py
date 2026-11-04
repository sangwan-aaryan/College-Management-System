from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import mysql
from ..forms import ChangePasswordForm, LoginForm
from ..models import User
from . import route


@route('/')
def index(): return render_template('index.html')

@route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        role = form.role.data
        cur = mysql.connection.cursor()
        if role == 'admin': cur.execute("SELECT * FROM admin WHERE admin_id = %s", (user_id,))
        elif role == 'teacher': cur.execute("SELECT * FROM teacher WHERE teacher_id = %s", (user_id,))
        elif role == 'student': cur.execute("SELECT * FROM student WHERE student_id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        if user_data and check_password_hash(user_data['password'], form.password.data):
            name = user_data.get('name') or user_data.get('admin_id')
            user = User(
                user_id=user_data[f'{role}_id'],
                name=name,
                role=role,
            )
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else: flash('Invalid User ID, password, or role.', 'danger')
    return render_template('login.html', form=form)

@route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('login'))

@route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.role == 'admin': flash('Use the set-admin-password command to update administrator credentials.', 'danger'); return redirect(url_for('dashboard'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        table = current_user.role; id_col = f"{table}_id"
        cur = mysql.connection.cursor(); cur.execute(f"SELECT password FROM {table} WHERE {id_col} = %s", (current_user.id,)); user_data = cur.fetchone()
        if user_data and check_password_hash(user_data['password'], form.old_password.data):
            hashed = generate_password_hash(form.new_password.data)
            cur.execute(f"UPDATE {table} SET password = %s WHERE {id_col} = %s", (hashed, current_user.id)); mysql.connection.commit(); flash('Password updated!', 'success'); return redirect(url_for('dashboard'))
        else: flash('Incorrect old password.', 'danger')
        cur.close()
    return render_template('change_password.html', form=form)

@route('/about')
def about(): return render_template('about.html')
