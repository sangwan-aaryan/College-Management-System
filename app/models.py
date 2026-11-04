from flask_login import UserMixin

from .extensions import login_manager, mysql


class User(UserMixin):
    def __init__(self, user_id, name, role):
        self.id = str(user_id)
        self.name = name
        self.role = role

    def get_id(self):
        return f"{self.role}:{self.id}"


@login_manager.user_loader
def load_user(user_id):
    role, separator, identifier = user_id.partition(":")
    if not separator:
        return None

    tables = {
        "admin": ("admin", "admin_id"),
        "teacher": ("teacher", "teacher_id"),
        "student": ("student", "student_id"),
    }
    if role not in tables:
        return None

    table, id_column = tables[role]
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            f"SELECT {id_column}, name FROM {table} WHERE {id_column} = %s",
            (identifier,),
        )
        user_data = cursor.fetchone()
    finally:
        cursor.close()

    if not user_data:
        return None

    return User(
        user_id=user_data[id_column],
        name=user_data.get("name") or user_data[id_column],
        role=role,
    )
