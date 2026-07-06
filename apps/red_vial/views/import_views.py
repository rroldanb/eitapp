import copy
import json
from datetime import date, time
from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from apps.proyectos.models import Mandante, Proyecto
from apps.red_vial.services.import_service import (
    _VirtualObj,
    analyze_parsed_data,
    execute_import,
    filter_by_dataset,
    parse_excel,
    reassign_to_project,
    validate_selection,
)

# Fields that must be restored to typed objects before execute_import
_RESTORE_TIME_FIELDS = {
    "Periodizacion": {"hora"},
    "Periodo": {"hora_inicio", "hora_fin"},
}
_RESTORE_DATE_FIELDS = {
    "Periodizacion": {"fecha"},
    "Proyecto": {"date_started"},
}

SESSION_PREFIX = "import_"


def _clear_import_session(request: HttpRequest) -> None:
    keys = [k for k in request.session.keys() if k.startswith(SESSION_PREFIX)]
    for k in keys:
        del request.session[k]


def _step_data(request: HttpRequest) -> dict[str, Any]:
    return {
        "parsed": request.session.get(f"{SESSION_PREFIX}parsed"),
        "filename": request.session.get(f"{SESSION_PREFIX}filename"),
        "selected": request.session.get(f"{SESSION_PREFIX}selected"),
        "validation": request.session.get(f"{SESSION_PREFIX}validation"),
        "report": request.session.get(f"{SESSION_PREFIX}report"),
    }


def _session_safe(obj: Any) -> Any:
    """Deep-convert non-JSON-serializable types to strings."""
    if isinstance(obj, (time, date)):
        return obj.isoformat()
    if isinstance(obj, _VirtualObj):
        return obj._value
    if isinstance(obj, Model):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _session_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_session_safe(v) for v in obj]
    return obj


def _restore_validation(validation: dict[str, Any]) -> dict[str, Any]:
    """Restore time/date strings in valid/duplicate rows for execute_import."""
    for sheet_name, result in validation.get("results", {}).items():
        for row in result.get("valid", []):
            for f in _RESTORE_TIME_FIELDS.get(sheet_name, set()):
                v = row.get(f)
                if isinstance(v, str):
                    try:
                        h, m = v.split(":")
                        if len(h) == 2 and 0 <= int(h) <= 23 and 0 <= int(m) <= 59:
                            row[f] = time(int(h), int(m))
                    except (ValueError, AttributeError):
                        pass
            for f in _RESTORE_DATE_FIELDS.get(sheet_name, set()):
                v = row.get(f)
                if isinstance(v, str):
                    try:
                        parts = v.split("-")
                        if len(parts) == 3:
                            row[f] = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    except (ValueError, AttributeError):
                        pass
        for row in result.get("duplicates", []):
            for f in _RESTORE_TIME_FIELDS.get(sheet_name, set()):
                v = row.get(f)
                if isinstance(v, str):
                    try:
                        h, m = v.split(":")
                        if len(h) == 2 and 0 <= int(h) <= 23 and 0 <= int(m) <= 59:
                            row[f] = time(int(h), int(m))
                    except (ValueError, AttributeError):
                        pass
            for f in _RESTORE_DATE_FIELDS.get(sheet_name, set()):
                v = row.get(f)
                if isinstance(v, str):
                    try:
                        parts = v.split("-")
                        if len(parts) == 3:
                            row[f] = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    except (ValueError, AttributeError):
                        pass
    return validation


STEPS_DATA = [
    (1, "Subir archivo"),
    (2, "Configurar"),
    (3, "Seleccionar hojas"),
    (4, "Validar"),
    (5, "Reporte"),
]


def _build_response(
    request: HttpRequest,
    proyecto: Proyecto | None,
    step: int,
    content_template: str,
    extra: dict[str, Any] | None = None,
) -> HttpResponse:
    data = _step_data(request)
    ctx = {
        "proyecto": proyecto,
        "current_step": step,
        "steps_data": STEPS_DATA,
        "parsed": data["parsed"],
        "filename": data["filename"],
        "selected": data["selected"],
        "validation": data["validation"],
        "report": data["report"],
        "report_totals": request.session.get(f"{SESSION_PREFIX}report_totals"),
        "report_json": json.dumps(data["report"] or {}),
        "report_totals_json": json.dumps(
            request.session.get(f"{SESSION_PREFIX}report_totals") or {}
        ),
        "analysis": request.session.get(f"{SESSION_PREFIX}analysis"),
        "proyectos": Proyecto.objects.filter(user=request.user).order_by("-created_at")
        if step == 2
        else None,
        "mandantes": Mandante.objects.all().order_by("name") if step == 2 else None,
    }
    if extra:
        ctx.update(extra)

    content_html = render_to_string(content_template, ctx)
    stepper_html = render_to_string("partials/Import/stepper.html", ctx)

    response = HttpResponse(
        content_html + '<div id="import-stepper-bar" hx-swap-oob="true">' + stepper_html + "</div>"
    )
    return response


# ── New entry point (replaces import_project_select) ──────────────────────────


@login_required
def import_landing(request: HttpRequest) -> HttpResponse:
    proyectos = Proyecto.objects.filter(user=request.user).order_by("-created_at")
    mandantes = Mandante.objects.all().order_by("name")
    _clear_import_session(request)
    return render(
        request,
        "red_vial/import_landing.html",
        {
            "proyecto": None,
            "current_step": 1,
            "steps_data": STEPS_DATA,
            "proyectos": proyectos,
            "mandantes": mandantes,
        },
    )


# ── Step 1: Upload file (no proyecto needed) ──────────────────────────────────


@login_required
@require_POST
def import_upload(request: HttpRequest) -> HttpResponse:
    _clear_import_session(request)

    excel_file = request.FILES.get("file")
    if not excel_file:
        return _build_response(
            request,
            None,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "Debes seleccionar un archivo Excel"},
        )

    if not excel_file.name.endswith((".xlsx", ".xls")):
        return _build_response(
            request,
            None,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "Solo se aceptan archivos .xlsx o .xls"},
        )

    try:
        parsed = parse_excel(excel_file)
    except Exception as e:
        return _build_response(
            request,
            None,
            1,
            "partials/Import/paso1_upload.html",
            {"error": f"Error al leer el archivo: {e}"},
        )

    if not parsed:
        return _build_response(
            request,
            None,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "El archivo no contiene datos válidos en ninguna hoja"},
        )

    request.session[f"{SESSION_PREFIX}parsed"] = parsed
    request.session[f"{SESSION_PREFIX}filename"] = excel_file.name

    # Analyze for multiple datasets
    analysis = analyze_parsed_data(parsed)
    request.session[f"{SESSION_PREFIX}analysis"] = analysis

    return _build_response(
        request, None, 2, "partials/Import/paso2_configurar.html", {"analysis": analysis}
    )


# ── Step 2: Configure dataset + project + mandante (no proyecto needed) ───────


@login_required
@require_POST
def import_configure(request: HttpRequest) -> HttpResponse:
    data = _step_data(request)
    parsed = data["parsed"]
    if not parsed:
        return _build_response(
            request,
            None,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "Sesión expirada. Vuelve a subir el archivo."},
        )

    analysis = request.session.get(f"{SESSION_PREFIX}analysis", [])
    dataset_title = request.POST.get("dataset_title", "")
    project_mode = request.POST.get("project_mode", "new")
    project_name = request.POST.get("project_name", "").strip()
    existing_project_id = request.POST.get("existing_project_id", "")
    project_description = request.POST.get("project_description", "").strip()
    project_date_started = request.POST.get("project_date_started", "").strip()
    mandante_mode = request.POST.get("mandante_mode", "existing")
    mandante_name = request.POST.get("mandante_name", "").strip()
    mandante_location = request.POST.get("mandante_location", "").strip()
    mandante_details = request.POST.get("mandante_details", "").strip()

    # Validate
    if not dataset_title and len(analysis) > 1:
        return _build_response(
            request,
            None,
            2,
            "partials/Import/paso2_configurar.html",
            {"error": "Debes seleccionar un conjunto de datos", "analysis": analysis},
        )

    if project_mode == "new" and not project_name:
        return _build_response(
            request,
            None,
            2,
            "partials/Import/paso2_configurar.html",
            {"error": "Debes indicar un nombre para el nuevo proyecto", "analysis": analysis},
        )

    if mandante_mode == "new" and not mandante_name:
        return _build_response(
            request,
            None,
            2,
            "partials/Import/paso2_configurar.html",
            {"error": "Debes indicar el nombre del mandante", "analysis": analysis},
        )

    # Create or get project
    try:
        if project_mode == "existing":
            proyecto = get_object_or_404(Proyecto, id=existing_project_id, user=request.user)
        else:
            # Create or reuse mandante
            if mandante_mode == "existing":
                mandante_id = request.POST.get("existing_mandante_id", "")
                mandante = get_object_or_404(Mandante, id=mandante_id)
            else:
                mandante, _ = Mandante.objects.get_or_create(
                    name=mandante_name,
                    defaults={"location": mandante_location, "details": mandante_details},
                )
            proyecto = Proyecto.objects.create(
                title=project_name,
                description=project_description,
                date_started=project_date_started or "2025-01-01",
                mandante=mandante,
                user=request.user,
            )
    except Exception as e:
        return _build_response(
            request,
            None,
            2,
            "partials/Import/paso2_configurar.html",
            {"error": f"Error al configurar el proyecto: {e}", "analysis": analysis},
        )

    # Store config choices in session
    request.session[f"{SESSION_PREFIX}dataset_title"] = dataset_title
    request.session[f"{SESSION_PREFIX}project_mode"] = project_mode
    request.session[f"{SESSION_PREFIX}mandante_mode"] = mandante_mode

    # Filter parsed data to only include rows for the selected dataset
    if dataset_title:
        parsed = filter_by_dataset(parsed, dataset_title)
        # Reassign all rows to point to the destination project
        reassign_to_project(parsed, proyecto.title)
        request.session[f"{SESSION_PREFIX}parsed"] = parsed

    return _build_response(request, proyecto, 3, "partials/Import/paso2_seleccion.html")


# ── Legacy entry point (sidebar / direct link) ────────────────────────────────


@login_required
def import_start(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    _clear_import_session(request)
    from_sidebar = request.GET.get("from_sidebar")
    if from_sidebar:
        request.session[f"{SESSION_PREFIX}from_sidebar"] = True
    return render(
        request,
        "red_vial/importar.html",
        {
            "proyecto": proyecto,
            "current_step": 1,
            "steps_data": STEPS_DATA,
        },
    )


# ── Step 3: Select sheets ─────────────────────────────────────────────────────


@login_required
@require_POST
def import_goto_selection(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    data = _step_data(request)
    if not data["parsed"]:
        return _build_response(
            request,
            proyecto,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "Sesión expirada. Vuelve a subir el archivo."},
        )
    return _build_response(
        request,
        proyecto,
        3,
        "partials/Import/paso2_seleccion.html",
        {"from_sidebar": request.session.get(f"{SESSION_PREFIX}from_sidebar")},
    )


# ── Back from selection to config ─────────────────────────────────────────────


@login_required
@require_POST
def import_back_config(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    keys = [
        k
        for k in request.session.keys()
        if k.startswith(f"{SESSION_PREFIX}selected")
        or k.startswith(f"{SESSION_PREFIX}validation")
        or k.startswith(f"{SESSION_PREFIX}report")
        or k.startswith(f"{SESSION_PREFIX}report_totals")
    ]
    for k in keys:
        del request.session[k]
    analysis = request.session.get(f"{SESSION_PREFIX}analysis", [])
    return _build_response(
        request, proyecto, 2, "partials/Import/paso2_configurar.html", {"analysis": analysis}
    )


# ── Back to step 1 (re-upload) ────────────────────────────────────────────────


@login_required
@require_POST
def import_back_upload(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    keys = [
        k
        for k in request.session.keys()
        if k.startswith(f"{SESSION_PREFIX}parsed")
        or k.startswith(f"{SESSION_PREFIX}filename")
        or k.startswith(f"{SESSION_PREFIX}selected")
        or k.startswith(f"{SESSION_PREFIX}validation")
        or k.startswith(f"{SESSION_PREFIX}report")
        or k.startswith(f"{SESSION_PREFIX}report_totals")
        or k.startswith(f"{SESSION_PREFIX}analysis")
    ]
    for k in keys:
        del request.session[k]
    return _build_response(
        request,
        proyecto,
        1,
        "partials/Import/paso1_upload.html",
        {"message": "Selecciona un archivo Excel para importar."},
    )


# ── Step 4: Validate ──────────────────────────────────────────────────────────


@login_required
@require_POST
def import_validate(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    data = _step_data(request)
    parsed = data["parsed"]
    if not parsed:
        return _build_response(
            request,
            proyecto,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "Sesión expirada. Vuelve a subir el archivo."},
        )

    selected = request.POST.getlist("sheets")
    if not selected:
        return _build_response(
            request,
            proyecto,
            3,
            "partials/Import/paso2_seleccion.html",
            {
                "error": "Debes seleccionar al menos una hoja",
                "from_sidebar": request.session.get(f"{SESSION_PREFIX}from_sidebar"),
            },
        )

    request.session[f"{SESSION_PREFIX}selected"] = selected
    validation = validate_selection(parsed, selected, proyecto)
    request.session[f"{SESSION_PREFIX}validation"] = _session_safe(validation)

    # Auto-execute if no errors and no duplicates
    if validation["total_errors"] == 0 and validation["total_duplicates"] == 0:
        try:
            report = execute_import(copy.deepcopy(validation), proyecto, request.user)
            total_inserted = sum(sr.get("inserted", 0) for sr in report.values())
            total_updated = sum(sr.get("updated", 0) for sr in report.values())
            total_skipped = sum(sr.get("skipped_duplicates", 0) for sr in report.values())
            total_rejected = sum(len(sr.get("rejected", [])) for sr in report.values())
            request.session[f"{SESSION_PREFIX}report"] = report
            request.session[f"{SESSION_PREFIX}report_totals"] = {
                "inserted": total_inserted,
                "updated": total_updated,
                "skipped": total_skipped,
                "rejected": total_rejected,
            }
        except Exception as e:
            return _build_response(
                request,
                proyecto,
                4,
                "partials/Import/paso3_validacion.html",
                {"error": f"Error durante la importación: {e}"},
            )
        return _build_response(request, proyecto, 5, "partials/Import/paso5_reporte.html")

    return _build_response(request, proyecto, 4, "partials/Import/paso3_validacion.html")


# ── Step 5: Execute → Report ──────────────────────────────────────────────────


@login_required
@require_POST
def import_execute(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    data = _step_data(request)
    validation = data["validation"]
    if not validation:
        return _build_response(
            request,
            proyecto,
            1,
            "partials/Import/paso1_upload.html",
            {"error": "Sesión expirada. Vuelve a empezar."},
        )

    validation = _restore_validation(copy.deepcopy(validation))

    update_duplicates = {}
    for key in request.POST:
        if key.startswith("dup_"):
            sheet = key[4:]
            update_duplicates[sheet] = request.POST[key] == "update"

    try:
        report = execute_import(
            copy.deepcopy(validation), proyecto, request.user, update_duplicates
        )
        total_inserted = sum(sr.get("inserted", 0) for sr in report.values())
        total_updated = sum(sr.get("updated", 0) for sr in report.values())
        total_skipped = sum(sr.get("skipped_duplicates", 0) for sr in report.values())
        total_rejected = sum(len(sr.get("rejected", [])) for sr in report.values())
        request.session[f"{SESSION_PREFIX}report"] = report
        request.session[f"{SESSION_PREFIX}report_totals"] = {
            "inserted": total_inserted,
            "updated": total_updated,
            "skipped": total_skipped,
            "rejected": total_rejected,
        }
    except Exception as e:
        return _build_response(
            request,
            proyecto,
            4,
            "partials/Import/paso3_validacion.html",
            {"error": f"Error durante la importación: {e}"},
        )

    return _build_response(request, proyecto, 5, "partials/Import/paso5_reporte.html")


# ── Cancel ────────────────────────────────────────────────────────────────────


@login_required
@require_POST
def import_cancel(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    _clear_import_session(request)
    return _build_response(
        request,
        proyecto,
        1,
        "partials/Import/paso1_upload.html",
        {"message": "Importación cancelada."},
    )


# ── Redirect old entry point to new landing ───────────────────────────────────


@login_required
def import_project_select(request: HttpRequest) -> HttpResponse:
    return redirect("import_landing")
