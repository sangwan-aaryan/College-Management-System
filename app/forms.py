from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (
    DateField,
    FieldList,
    FormField,
    HiddenField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    ValidationError,
)

from .extensions import mysql


class LoginForm(FlaskForm):
    user_id = StringField("User ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    role = SelectField(
        "Role",
        choices=[("admin", "Admin"), ("teacher", "Teacher"), ("student", "Student")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Login")


class StudentForm(FlaskForm):
    student_id = StringField(
        "Student ID", validators=[DataRequired(), Length(max=20)]
    )
    name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=100)]
    )
    dob = DateField("Date of Birth", validators=[DataRequired()])
    course_id = SelectField("Course", coerce=str, validators=[DataRequired()])
    submit = SubmitField("Save Student")

    def validate_student_id(self, field):
        if request.endpoint != "add_student":
            return
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM student WHERE student_id = %s", (field.data,)
            )
            if cursor.fetchone():
                raise ValidationError("Student ID already exists.")
        finally:
            cursor.close()


class TeacherForm(FlaskForm):
    teacher_id = StringField(
        "Teacher ID", validators=[DataRequired(), Length(max=20)]
    )
    name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=100)]
    )
    course_id = SelectField(
        "Department (Course)", coerce=str, validators=[DataRequired()]
    )
    submit = SubmitField("Save Teacher")

    def validate_teacher_id(self, field):
        if request.endpoint != "add_teacher":
            return
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM teacher WHERE teacher_id = %s", (field.data,)
            )
            if cursor.fetchone():
                raise ValidationError("Teacher ID already exists.")
        finally:
            cursor.close()


class CourseForm(FlaskForm):
    course_id = StringField("Course ID", validators=[DataRequired(), Length(max=20)])
    course_name = StringField(
        "Course Name", validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField("Save Course")

    def validate_course_id(self, field):
        if request.endpoint != "add_course":
            return
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT 1 FROM course WHERE course_id = %s", (field.data,))
            if cursor.fetchone():
                raise ValidationError("Course ID already exists.")
        finally:
            cursor.close()


class SubjectForm(FlaskForm):
    subject_id = StringField(
        "Subject ID", validators=[DataRequired(), Length(max=20)]
    )
    subject_name = StringField(
        "Subject Name", validators=[DataRequired(), Length(max=100)]
    )
    course_id = SelectField("Course", coerce=str, validators=[DataRequired()])
    teacher_id = SelectField("Teacher", coerce=str, validators=[DataRequired()])
    submit = SubmitField("Save Subject")

    def validate_subject_id(self, field):
        if request.endpoint != "add_subject":
            return
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM subject WHERE subject_id = %s", (field.data,)
            )
            if cursor.fetchone():
                raise ValidationError("Subject ID already exists.")
        finally:
            cursor.close()


class NoticeForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post Notice")


class UploadFileForm(FlaskForm):
    file = FileField(
        "Excel File",
        validators=[FileRequired(), FileAllowed(["xlsx"], "Excel files only!")],
    )
    submit = SubmitField("Upload Data")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("new_password")],
    )
    submit = SubmitField("Update Password")


class StudentAttendanceForm(FlaskForm):
    student_id = HiddenField("Student ID")
    status = RadioField(
        "Status",
        choices=[("Present", "Present"), ("Absent", "Absent")],
        validators=[DataRequired()],
    )

    class Meta:
        csrf = False


class AttendanceForm(FlaskForm):
    students = FieldList(FormField(StudentAttendanceForm), min_entries=0)
    submit = SubmitField("Save Attendance")


class StudentMarksForm(FlaskForm):
    student_id = HiddenField("Student ID")
    marks = IntegerField("Marks", validators=[NumberRange(min=0, max=100)])

    class Meta:
        csrf = False


class MarksForm(FlaskForm):
    students = FieldList(FormField(StudentMarksForm), min_entries=0)
    submit = SubmitField("Save Marks")


__all__ = [
    "AttendanceForm",
    "ChangePasswordForm",
    "CourseForm",
    "LoginForm",
    "MarksForm",
    "NoticeForm",
    "StudentForm",
    "SubjectForm",
    "TeacherForm",
    "UploadFileForm",
]
