from flask import render_template


def page_not_found(error):
    return render_template("index.html", error="404"), 404


def internal_server_error(error):
    return render_template("index.html", error="500"), 500


def register_error_handlers(app):
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
