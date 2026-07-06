import os
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AdminUserCreationForm,
    AuthenticationForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.db import IntegrityError, connection, connections
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.common.db_router import get_active_db
from apps.usuarios.models import Role

LANG_MAP = {
    "es": "README.md",
    "en": "README.en.md",
    "pt": "README.pt-br.md",
}


@require_GET
def docs_api_view(request: HttpRequest, lang: str = "es") -> JsonResponse:
    filename = LANG_MAP.get(lang, "README.md")
    readme_path = os.path.join(settings.BASE_DIR, filename)
    try:
        with open(readme_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = f"# {lang.upper()} · Not found\n\nDocumentation not available in this language."
    return JsonResponse({"content": content})


def docs_view(request: HttpRequest, lang: str = "es") -> HttpResponse:
    return render(request, "docs.html", {"lang": lang})


@csrf_exempt
@require_GET
def healthcheck_view(request: HttpRequest) -> JsonResponse:
    """Check connectivity and status of all configured databases.

    Returns a JSON with per-alias status, migration count, and overall
    healthy/degraded status.  Intended for monitoring (load-balancer,
    docker healthcheck, uptime robot, etc.).
    """
    import time

    overall = "healthy"
    status: dict[str, Any] = {}

    for alias in settings.DATABASES:
        db_info: dict[str, Any] = {
            "engine": settings.DATABASES[alias].get("ENGINE", "unknown"),
            "name": settings.DATABASES[alias].get("NAME", ""),
            "host": settings.DATABASES[alias].get("HOST", ""),
            "port": settings.DATABASES[alias].get("PORT", ""),
        }
        try:
            t0 = time.monotonic()
            conn = connections[alias]
            conn.ensure_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                migration_count = cursor.fetchone()[0]
            db_info["latency_ms"] = round((time.monotonic() - t0) * 1000, 1)
            db_info["migrations"] = migration_count
            db_info["status"] = "ok"
        except Exception as exc:
            db_info["status"] = "error"
            db_info["error"] = str(exc)
            overall = "degraded"

        status[alias] = db_info

    status["_active_db"] = get_active_db() or "default"
    status["_overall"] = overall

    http_code = 200 if overall == "healthy" else 503
    return JsonResponse(status, status=http_code)


def handler404_view(request: HttpRequest, exception: Any = None) -> HttpResponse:
    return render(request, "404.html", status=404)


def switch_db(request: HttpRequest, alias: str) -> HttpResponse:
    if alias in settings.DATABASES:
        request.session["active_db"] = alias if alias != "default" else None
    return redirect(request.META.get("HTTP_REFERER", "home"))


def home(request: HttpRequest) -> HttpResponse:
    db_info = {
        "alias": request.session.get("active_db") or "default",
        "engine": connection.vendor,
        "host": connection.settings_dict.get("HOST", ""),
        "port": connection.settings_dict.get("PORT", ""),
        "name": connection.settings_dict.get("NAME", ""),
    }
    context = {
        "current_date": timezone.now(),
        "db_info": db_info,
        "databases": {k: v for k, v in settings.DATABASES.items() if k != "default"},
    }
    if request.user.is_authenticated:
        from django.db.models import Count

        from apps.mandantes.models import Mandante
        from apps.proyectos.models.proyecto import Proyecto
        from apps.red_vial.models.arco import Arco
        from apps.red_vial.models.calle import Calle
        from apps.red_vial.models.nodo import Nodo
        from apps.red_vial.models.periodo import Periodo
        from apps.red_vial.models.punto_control import PuntoControl

        context["proyectos_count"] = Proyecto.objects.filter(is_completed=False).count()
        context["proyectos_total"] = Proyecto.objects.count()
        context["mandantes_count"] = Mandante.objects.count()
        context["puntos_control_count"] = PuntoControl.objects.count()
        context["calles_count"] = Calle.objects.count()
        context["nodos_count"] = Nodo.objects.count()
        context["arcos_count"] = Arco.objects.count()
        context["periodos_count"] = Periodo.objects.count()
        context["proyecto_arcos_stats"] = list(
            Proyecto.objects.annotate(total_arcos=Count("arcos")).order_by("-total_arcos")[:3]
        )
        context["recent_projects"] = (
            Proyecto.objects.all().select_related("mandante").order_by("-created_at")[:5]
        )
    return render(request, "home.html", context)


def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "signup.html", {"form": UserCreationForm})

    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"], password=request.POST["password1"]
                )
                user.save()
                login(request, user)
                return redirect("home")
            except IntegrityError:
                return render(
                    request,
                    "signup.html",
                    {"form": UserCreationForm, "error": "Username already exists"},
                )

        else:
            return render(
                request,
                "signup.html",
                {"form": UserCreationForm, "error": "Passwords do not match"},
            )


def signin(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST["username"], password=request.POST["password"]
        )
        if user is not None:
            login(request, user)
            request.session["show_pending_modal"] = True
            return redirect(request.GET.get("next", "home"))
        else:
            return render(
                request,
                "signin.html",
                {"form": AuthenticationForm, "error": "Invalid username or password"},
            )


@login_required
def signout(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home")


@staff_member_required
def admin_create_user_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_value = int(request.POST.get("role", Role.ENCUESTADOR))
            if hasattr(user, "profile"):
                user.profile.role = role_value
                user.profile.save()
            messages.success(
                request, f'Usuario "{user.username}" creado con rol {Role(role_value).label}.'
            )
            return redirect("user_management")
        return render(request, "admin_create_user.html", {"form": form})
    return redirect("user_management")


@staff_member_required
def user_management_view(request: HttpRequest) -> HttpResponse:
    sort_map = {
        "username": "username",
        "role": "profile__role",
        "is_active": "is_active",
    }
    sort_by = request.GET.get("sort_by", "role")
    sort_order = request.GET.get("sort_order", "desc")
    if sort_by not in sort_map:
        sort_by = "role"
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    order_prefix = "-" if sort_order == "desc" else ""
    users = (
        User.objects.all()
        .select_related("profile")
        .order_by(f"{order_prefix}{sort_map[sort_by]}", "username")
    )
    context = {"users": users, "sort_by": sort_by, "sort_order": sort_order}
    if request.headers.get("HX-Request"):
        return render(request, "_user_table.html", context)
    return render(request, "user_management.html", context)


@staff_member_required
@require_POST
def user_toggle_active_view(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "No puedes deshabilitarte a ti mismo.")
    else:
        user.is_active = not user.is_active
        user.save()
        action = "habilitado" if user.is_active else "deshabilitado"
        messages.success(request, f'Usuario "{user.username}" {action}.')
    return redirect("user_management")


@staff_member_required
@require_POST
def user_change_role_view(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "No puedes cambiar tu propio rol.")
    else:
        new_role = int(request.POST.get("role", Role.ENCUESTADOR))
        if hasattr(user, "profile"):
            user.profile.role = new_role
            user.profile.save()
        messages.success(request, f'Rol de "{user.username}" actualizado a {Role(new_role).label}.')
    return redirect("user_management")


@staff_member_required
def user_change_password_view(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contraseña de "{user.username}" actualizada.')
            return redirect("user_management")
    else:
        form = SetPasswordForm(user)
    return render(request, "user_change_password.html", {"form": form, "target_user": user})
