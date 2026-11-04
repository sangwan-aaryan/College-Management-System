from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask
from werkzeug.security import generate_password_hash

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .config import Config
from .extensions import login_manager, mysql


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be configured in the project .env file.")
    if not app.config.get("INITIAL_USER_PASSWORD"):
        raise RuntimeError(
            "INITIAL_USER_PASSWORD must be configured in the project .env file."
        )
    if len(app.config["SECRET_KEY"]) < 32:
        raise RuntimeError("SECRET_KEY must contain at least 32 characters.")
    if len(app.config["INITIAL_USER_PASSWORD"]) < 12:
        raise RuntimeError(
            "INITIAL_USER_PASSWORD must contain at least 12 characters."
        )
    if app.config["SESSION_COOKIE_SAMESITE"] not in {"Lax", "Strict", "None"}:
        raise RuntimeError(
            "SESSION_COOKIE_SAMESITE must be Lax, Strict, or None."
        )
    if (
        app.config["SESSION_COOKIE_SAMESITE"] == "None"
        and not app.config["SESSION_COOKIE_SECURE"]
    ):
        raise RuntimeError(
            "SESSION_COOKIE_SECURE must be enabled when SESSION_COOKIE_SAMESITE=None."
        )

    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message_category = "danger"

    from .routes import register_routes

    register_routes(app)
    register_cli_commands(app)
    return app


def register_cli_commands(app):
    @app.cli.command("serve")
    def serve():
        """Run the development server using the project .env settings."""
        app.run(
            host=app.config["FLASK_HOST"],
            port=app.config["FLASK_PORT"],
            debug=app.config["DEBUG"],
        )

    @app.cli.command("create-admin")
    @click.option("--admin-id", prompt="Admin ID")
    @click.option("--name", prompt="Admin name")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(admin_id, name, password):
        """Create an administrator account with a hashed password."""
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO admin (admin_id, name, password) VALUES (%s, %s, %s)",
                (admin_id, name, generate_password_hash(password)),
            )
            mysql.connection.commit()
        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cursor.close()
        click.echo(f"Administrator {admin_id} created.")

    @app.cli.command("set-admin-password")
    @click.option("--admin-id", prompt="Admin ID")
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    )
    def set_admin_password(admin_id, password):
        """Set an administrator password using a secure password hash."""
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "UPDATE admin SET password = %s WHERE admin_id = %s",
                (generate_password_hash(password), admin_id),
            )
            if cursor.rowcount == 0:
                raise click.ClickException(f"Administrator {admin_id} was not found.")
            mysql.connection.commit()
        except Exception:
            mysql.connection.rollback()
            raise
        finally:
            cursor.close()
        click.echo(f"Password updated for administrator {admin_id}.")


__all__ = ["create_app"]
