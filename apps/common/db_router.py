import threading
from typing import Any

from django.conf import settings
from django.db.models import Model

_active_db = threading.local()


def set_active_db(alias: str) -> None:
    if alias in settings.DATABASES:
        _active_db.alias = alias


def get_active_db() -> str | None:
    return getattr(_active_db, "alias", None)


def clear_active_db() -> None:
    _active_db.alias = None


class ActiveDatabaseRouter:
    def db_for_read(self, model: type[Model], **hints: Any) -> str | None:
        if model._meta.app_label == "sessions":
            return None
        return get_active_db() or None

    def db_for_write(self, model: type[Model], **hints: Any) -> str | None:
        if model._meta.app_label == "sessions":
            return None
        return get_active_db() or None

    def allow_relation(self, obj1: Model, obj2: Model, **hints: Any) -> bool | None:
        return None

    def allow_migrate(
        self, db: str, app_label: str, model_name: str | None = None, **hints: Any
    ) -> bool | None:
        return None


class DatabaseSelectorMiddleware:
    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        alias = request.session.get("active_db")
        if alias:
            set_active_db(alias)
        try:
            return self.get_response(request)
        finally:
            clear_active_db()
