ROUTES = []


def route(rule, **options):
    """Keep the original endpoint names while registering routes via the factory."""
    def register(view):
        ROUTES.append((rule, view, options))
        return view

    return register


def register_routes(app):
    from . import academic_routes, admin_routes, auth_routes, dashboard_routes
    from .main import register_error_handlers

    for rule, view, options in ROUTES:
        app.add_url_rule(
            rule,
            endpoint=view.__name__,
            view_func=view,
            **options,
        )
    register_error_handlers(app)
