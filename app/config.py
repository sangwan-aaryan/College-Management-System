import os


def env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"1", "true", "yes", "on", "0", "false", "no", "off"}:
        raise ValueError(f"{name} must be a boolean value.")
    return normalized in {"1", "true", "yes", "on"}


def env_int(name, default, minimum):
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError as error:
        raise ValueError(f"{name} must be an integer.") from error
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}.")
    return value


class Config:
    DEBUG = env_bool("FLASK_DEBUG", False)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    INITIAL_USER_PASSWORD = os.environ.get("INITIAL_USER_PASSWORD")
    FLASK_HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = env_int("FLASK_PORT", 5000, 1)
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = env_int("MYSQL_PORT", 3306, 1)
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "college_db")
    MYSQL_CURSORCLASS = "DictCursor"
    MAX_UPLOAD_SIZE_MB = env_int("MAX_UPLOAD_SIZE_MB", 10, 1)
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
    SESSION_COOKIE_HTTPONLY = env_bool("SESSION_COOKIE_HTTPONLY", True)
    SESSION_COOKIE_SAMESITE = os.environ.get(
        "SESSION_COOKIE_SAMESITE", "Lax"
    ).capitalize()
    WTF_CSRF_ENABLED = env_bool("WTF_CSRF_ENABLED", True)
