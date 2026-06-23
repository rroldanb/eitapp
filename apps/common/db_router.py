import threading
from django.conf import settings

_active_db = threading.local()


def set_active_db(alias):
    if alias in settings.DATABASES:
        _active_db.alias = alias


def get_active_db():
    return getattr(_active_db, 'alias', None)


def clear_active_db():
    _active_db.alias = None


class ActiveDatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'sessions':
            return None
        return get_active_db() or None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'sessions':
            return None
        return get_active_db() or None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return None


class DatabaseSelectorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        alias = request.session.get('active_db')
        if alias:
            set_active_db(alias)
        try:
            return self.get_response(request)
        finally:
            clear_active_db()
