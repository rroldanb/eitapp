import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, QueryDict
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View

from apps.proyectos.models import Proyecto
from apps.red_vial.forms.periodizacion_forms import PeriodizacionForm
from apps.red_vial.models import Nodo, Periodizacion, Periodo, PuntoControl
from apps.red_vial.services.periodizacion_service import (
    delete_periodizacion,
    generar_filas,
    get_periodizaciones,
    update_periodizacion,
)


@method_decorator(login_required, name="dispatch")
class PeriodizacionListView(View):
    """Lista de periodización con filtros y generación de filas."""

    template_full = "red_vial/periodizacion_list.html"
    template_container = "partials/Periodizacion/periodizacion_container.html"

    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        nodo_ids = request.GET.getlist("nodo")
        periodo_ids = request.GET.getlist("periodo")
        movimiento_ids = request.GET.getlist("movimiento")
        fecha: str | None = request.GET.get("fecha") or None
        sort_param = request.GET.get("sort")
        order_param = request.GET.get("order", "asc")

        nodo_ids = [n for n in nodo_ids if n]
        periodo_ids = [p for p in periodo_ids if p]
        movimiento_ids = [m for m in movimiento_ids if m]

        rows = get_periodizaciones(
            proyecto_id=proyecto_id,
            nodo_ids=nodo_ids or None,
            periodo_ids=periodo_ids or None,
            movimiento_ids=movimiento_ids or None,
            fecha=fecha,
            sort_param=sort_param,
            order_param=order_param,
        )

        available_nodos = (
            Nodo.objects.filter(numero_pc__isnull=False, proyecto=proyecto)
            .select_related("calle_1", "calle_2")
            .order_by("numero_pc")
        )
        available_periodos = Periodo.objects.filter(proyecto=proyecto)

        available_fechas = (
            Periodizacion.objects.filter(pc__proyecto=proyecto)
            .values_list("fecha", flat=True)
            .distinct()
            .order_by("-fecha")
        )

        pc_qs = PuntoControl.objects.filter(proyecto=proyecto)
        if nodo_ids:
            pc_qs = pc_qs.filter(nodo_id__in=nodo_ids)
        available_movimiento_values = (
            pc_qs.values_list("movimiento", flat=True).distinct().order_by("movimiento")
        )
        movimiento_choices_dict = dict(PuntoControl.Movimiento.choices)
        available_movimientos = [
            {"value": v, "label": movimiento_choices_dict.get(v, v)}
            for v in available_movimiento_values
        ]

        context = {
            "proyecto": proyecto,
            "rows": rows,
            "available_nodos": available_nodos,
            "available_periodos": available_periodos,
            "available_fechas": available_fechas,
            "available_movimientos": available_movimientos,
            "selected_nodos": nodo_ids,
            "selected_periodos": periodo_ids,
            "selected_movimientos": movimiento_ids,
            "selected_fecha": fecha,
            "sort_param": sort_param,
            "order_param": order_param,
            "form": PeriodizacionForm(),
        }

        if request.headers.get("HX-Request"):
            return render(request, self.template_container, context)
        return render(request, self.template_full, context)

    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        """Genera filas de periodización."""
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        nodo_ids = data.getlist("nodo") if hasattr(data, "getlist") else data.get("nodo_ids", [])
        periodo_ids = (
            data.getlist("periodo") if hasattr(data, "getlist") else data.get("periodo_ids", [])
        )
        movimiento_ids = (
            data.getlist("movimiento")
            if hasattr(data, "getlist")
            else data.get("movimiento_ids", [])
        )
        fecha = data.get("fecha_generar") or data.get("fecha")

        nodo_ids = [n for n in nodo_ids if n]
        periodo_ids = [p for p in periodo_ids if p]
        movimiento_ids = [m for m in movimiento_ids if m]

        if not nodo_ids or not periodo_ids or not fecha:
            return HttpResponseBadRequest(
                json.dumps({"error": "Debe seleccionar PC(s), Periodo(s) y Fecha"}),
                content_type="application/json",
            )

        try:
            count = generar_filas(proyecto, nodo_ids, periodo_ids, fecha, movimiento_ids or None)
            rows = get_periodizaciones(
                proyecto_id=proyecto_id,
                nodo_ids=nodo_ids,
                periodo_ids=periodo_ids,
                movimiento_ids=movimiento_ids or None,
                fecha=fecha,
            )
            available_fechas = (
                Periodizacion.objects.filter(pc__proyecto=proyecto)
                .values_list("fecha", flat=True)
                .distinct()
                .order_by("-fecha")
            )
            pc_qs = PuntoControl.objects.filter(proyecto=proyecto)
            if nodo_ids:
                pc_qs = pc_qs.filter(nodo_id__in=nodo_ids)
            available_movimiento_values = (
                pc_qs.values_list("movimiento", flat=True).distinct().order_by("movimiento")
            )
            movimiento_choices_dict = dict(PuntoControl.Movimiento.choices)
            available_movimientos = [
                {"value": v, "label": movimiento_choices_dict.get(v, v)}
                for v in available_movimiento_values
            ]
            context = {
                "proyecto": proyecto,
                "rows": rows,
                "available_nodos": Nodo.objects.filter(
                    numero_pc__isnull=False, proyecto=proyecto
                ).select_related("calle_1", "calle_2"),
                "available_periodos": Periodo.objects.filter(proyecto=proyecto),
                "available_fechas": available_fechas,
                "available_movimientos": available_movimientos,
                "selected_nodos": nodo_ids,
                "selected_periodos": periodo_ids,
                "selected_movimientos": movimiento_ids,
                "selected_fecha": fecha,
                "form": PeriodizacionForm(),
                "generated_count": count,
            }
            response = render(request, self.template_container, context)
            response["X-Generated-Count"] = str(count)
            return response
        except IntegrityError:
            return HttpResponseBadRequest(
                json.dumps({"error": "Error de integridad al generar filas."}),
                content_type="application/json",
            )


@method_decorator(login_required, name="dispatch")
class PeriodizacionUpdateView(View):
    """Actualiza un campo vehicular de una fila de periodización (PUT parcial)."""

    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                data = QueryDict(request.body).dict()
            item = update_periodizacion(item_id, data)
            context = {
                "item": item,
                "form": PeriodizacionForm(instance=item),
            }
            return render(request, "partials/Periodizacion/periodizacion_row.html", context)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({"error": str(e)}),
                content_type="application/json",
            )


@method_decorator(login_required, name="dispatch")
class PeriodizacionDeleteView(View):
    """Elimina una fila de periodización."""

    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            delete_periodizacion(item_id)
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({"error": str(e)}),
                content_type="application/json",
            )
