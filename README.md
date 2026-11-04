# College Management System

A server-rendered college administration portal built with Flask and MySQL. It
provides separate workflows for administrators, teachers, and students.

## Features

- Role-based sign-in and dashboards for admins, teachers, and students
- Student, teacher, course, and subject management
- Spreadsheet imports for students, teachers, courses, and subjects
- Teacher attendance and marks entry
- Student attendance history and results
- Notice board and password changes for student and teacher accounts
- CSRF-protected forms, hashed passwords, and environment-based configuration

## Project structure

```text
app/
  __init__.py          Application factory and Flask CLI commands
  config.py            Environment-backed application configuration
  extensions.py        Flask extensions
  forms.py             WTForms definitions and validation
  models.py            Login user model and user loader
  services.py          Spreadsheet imports and password helpers
  routes/
    auth_routes.py
    dashboard_routes.py
    admin_routes.py
    academic_routes.py
    main.py             HTTP error handlers
  templates/           Jinja templates
  static/               CSS, JavaScript, and uploads
database/
  schema.sql            MySQL schema for a new database
tests/
run.py                  Flask CLI and local development entry point
```

## Requirements

- Python 3.10 or later
- MySQL 8.0 or later

## Local setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`. Set a unique `SECRET_KEY`, a strong
   `INITIAL_USER_PASSWORD`, and your MySQL connection settings. Generate a secret
   key with:

   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   The application loads `.env` from the project root. Variables already set in
   the process environment take precedence.

4. Create the database and tables by running `database/schema.sql` in MySQL.
5. Create an administrator account:

   ```powershell
   flask --app run create-admin
   ```

6. Start the local development server:

   ```powershell
   python run.py
   ```

   Alternatively, run `flask --app run serve`. Set `FLASK_DEBUG=1` only for local
   development.

## Environment configuration

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Flask session and CSRF signing key; required, at least 32 characters | None |
| `INITIAL_USER_PASSWORD` | Initial password for newly created student and teacher accounts; required, at least 12 characters | None |
| `FLASK_HOST` | Address used by the local development server | `127.0.0.1` |
| `FLASK_PORT` | Local development server port | `5000` |
| `FLASK_DEBUG` | Enable Flask debug mode | `0` |
| `MYSQL_HOST` | MySQL server host | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | Empty |
| `MYSQL_DB` | MySQL database name | `college_db` |
| `MAX_UPLOAD_SIZE_MB` | Maximum request/upload size in megabytes | `10` |
| `SESSION_COOKIE_SECURE` | Only send session cookies over HTTPS | `0` |
| `SESSION_COOKIE_HTTPONLY` | Prevent JavaScript access to session cookies | `1` |
| `SESSION_COOKIE_SAMESITE` | Session-cookie cross-site policy: `Lax`, `Strict`, or `None` | `Lax` |
| `WTF_CSRF_ENABLED` | Enable Flask-WTF CSRF protection | `1` |

For HTTPS deployments, set `SESSION_COOKIE_SECURE=1`. `SESSION_COOKIE_SAMESITE=None`
also requires secure cookies.

New student and teacher accounts receive the configured initial password. Ask
users to change it after signing in. To update an administrator password:

```powershell
flask --app run set-admin-password
```

## Tests

Run the database-independent test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Database notes

`database/schema.sql` is intended for a new database. Back up an existing
database before migrating or replacing its schema. The schema does not insert a
default administrator; create one with the Flask CLI after setup.
