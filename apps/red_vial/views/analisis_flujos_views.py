import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

from apps.proyectos.models import Proyecto
from apps.red_vial.models import Nodo, Periodizacion, Periodo, PuntoControl
from apps.red_vial.services.resumen_flujo_service import (
    get_analisis_flujos,
    get_chart_data,
    get_comparison,
    get_detalle_horario,
    get_detalle_horario_chart_data,
    get_detalle_por_pc_chart_data,
    get_ranking,
    recalcular_resumenes,
)


@method_decorator(login_required, name="dispatch")
class AnalisisFlujosView(View):
    template_full = "red_vial/analisis_flujos.html"
    template_container = "partials/analisis_flujos/analisis_flujos_container.html"

    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        nodo_ids = request.GET.getlist("nodo")
        periodo_ids = request.GET.getlist("periodo")
        movimiento_ids = request.GET.getlist("movimiento")
        fecha = request.GET.get("fecha") or None

        nodo_ids = [n for n in nodo_ids if n]
        periodo_ids = [p for p in periodo_ids if p]
        movimiento_ids = [m for m in movimiento_ids if m]

        available_nodos = (
            Nodo.objects.filter(numero_pc__isnull=False, proyecto=proyecto)
            .select_related("calle_1", "calle_2")
            .order_by("numero_pc")
        )
        all_periodos = list(Periodo.objects.filter(proyecto=proyecto))

        available_fechas = (
            Periodizacion.objects.filter(pc__proyecto=proyecto)
            .values_list("fecha", flat=True)
            .distinct()
            .order_by("-fecha")
        )

        mov_qs = PuntoControl.objects.filter(proyecto=proyecto)
        if nodo_ids:
            mov_qs = mov_qs.filter(nodo_id__in=nodo_ids)
        available_movimiento_values = (
            mov_qs.values_list("movimiento", flat=True).distinct().order_by("movimiento")
        )
        movimiento_choices_dict = dict(PuntoControl.Movimiento.choices)
        available_movimientos = [
            {"value": v, "label": movimiento_choices_dict.get(v, v)}
            for v in available_movimiento_values
        ]

        # Resolve nodo_ids + movimiento_ids to PuntoControl IDs
        pc_qs = PuntoControl.objects.filter(proyecto=proyecto)
        if nodo_ids:
            pc_qs = pc_qs.filter(nodo_id__in=nodo_ids)
        if movimiento_ids:
            pc_qs = pc_qs.filter(movimiento__in=movimiento_ids)
        pc_ids = list(pc_qs.values_list("id", flat=True))

        # Get analysis data
        analisis_data = get_analisis_flujos(
            proyecto_id=proyecto_id,
            pc_ids=pc_ids or None,
            periodo_ids=periodo_ids or None,
            fecha=fecha,
        )

        ranking = get_ranking(analisis_data)
        comparison = get_comparison(analisis_data, all_periodos)
        chart_data = get_chart_data(analisis_data, all_periodos)

        sort_by_detail = request.GET.get("sort_by_detail", "")
        sort_order_detail = request.GET.get("sort_order_detail", "asc")
        sort_by_resumen = request.GET.get("sort_by_resumen", "")
        sort_order_resumen = request.GET.get("sort_order_resumen", "asc")
        sort_by_ranking = request.GET.get("sort_by_ranking", "")
        sort_order_ranking = request.GET.get("sort_order_ranking", "asc")
        sort_by_comparison = request.GET.get("sort_by_comparison", "")
        sort_order_comparison = request.GET.get("sort_order_comparison", "asc")

        detalle_horario = get_detalle_horario(
            proyecto_id=proyecto_id,
            pc_ids=pc_ids or None,
            periodo_ids=periodo_ids or None,
            fecha=fecha,
            movimiento_ids=movimiento_ids or None,
        )
        detalle_horario_chart = get_detalle_horario_chart_data(detalle_horario)

        # Sort in-memory lists for table display
        sort_keys_detail = {
            "hora": lambda r: r["hora"],
            "flujo_15min": lambda r: r.get("flujo_15min", 0) or 0,
            "hora_movil": lambda r: r.get("hora_movil", 0) or 0,
            "es_punta": lambda r: r.get("es_punta", ""),
        }
        key_fn = sort_keys_detail.get(sort_by_detail)
        if key_fn:
            detalle_horario.sort(key=key_fn, reverse=sort_order_detail == "desc")

        sort_keys_resumen = {
            "pc_nombre": lambda r: r.get("pc_nombre", ""),
            "movimiento": lambda r: r.get("movimiento", ""),
            "periodo_codigo": lambda r: r.get("periodo_codigo", ""),
            "flujo_total": lambda r: r.get("flujo_total", 0) or 0,
            "promedio": lambda r: r.get("promedio", 0) or 0,
            "num_registros": lambda r: r.get("num_registros", 0) or 0,
        }
        key_fn = sort_keys_resumen.get(sort_by_resumen)
        if key_fn:
            analisis_data.sort(key=key_fn, reverse=sort_order_resumen == "desc")

        sort_keys_ranking = {
            "rank": lambda r: r.get("rank", 0) or 0,
            "pc_nombre": lambda r: r.get("pc_nombre", ""),
            "movimiento": lambda r: r.get("movimiento", ""),
            "total_flujo": lambda r: r.get("total_flujo", 0) or 0,
        }
        key_fn = sort_keys_ranking.get(sort_by_ranking)
        if key_fn:
            ranking.sort(key=key_fn, reverse=sort_order_ranking == "desc")

        sort_keys_comparison = {
            "pc_nombre": lambda r: r.get("pc_nombre", ""),
            "movimiento": lambda r: r.get("movimiento", ""),
        }
        # For period column sorting, dynamic key using period UUID string
        key_fn = sort_keys_comparison.get(sort_by_comparison)
        if key_fn:
            comparison.sort(key=key_fn, reverse=sort_order_comparison == "desc")
        elif sort_by_comparison:
            # Try sorting by a period column (UUID string key)
            try:
                pid = sort_by_comparison
                comparison.sort(
                    key=lambda r: r.get(pid, 0) or 0,
                    reverse=sort_order_comparison == "desc",
                )
            except Exception:
                pass

        per_pc_charts = get_detalle_por_pc_chart_data(
            proyecto_id=proyecto_id,
            pc_ids=pc_ids or None,
            periodo_ids=periodo_ids or None,
            fecha=fecha,
            movimiento_ids=movimiento_ids or None,
        )

        context = {
            "proyecto": proyecto,
            "available_nodos": available_nodos,
            "available_periodos": all_periodos,
            "available_fechas": available_fechas,
            "available_movimientos": available_movimientos,
            "selected_nodos": nodo_ids,
            "selected_periodos": periodo_ids,
            "selected_movimientos": movimiento_ids,
            "selected_fecha": fecha,
            "analisis_data": analisis_data,
            "ranking": ranking,
            "comparison": comparison,
            "comparison_periodos": all_periodos,
            "chart_data_json": json.dumps(chart_data),
            "total_records": len(analisis_data),
            "detalle_horario": detalle_horario,
            "detalle_horario_chart_json": json.dumps(detalle_horario_chart),
            "per_pc_charts": per_pc_charts,
            "per_pc_charts_json": json.dumps(per_pc_charts),
            "sort_by_detail": sort_by_detail,
            "sort_order_detail": sort_order_detail,
            "sort_by_resumen": sort_by_resumen,
            "sort_order_resumen": sort_order_resumen,
            "sort_by_ranking": sort_by_ranking,
            "sort_order_ranking": sort_order_ranking,
            "sort_by_comparison": sort_by_comparison,
            "sort_order_comparison": sort_order_comparison,
        }

        if request.headers.get("HX-Request"):
            if any(k.startswith("sort_by_") for k in request.GET):
                return render(
                    request, "partials/analisis_flujos/analisis_flujos_content.html", context
                )
            return render(request, self.template_container, context)
        return render(request, self.template_full, context)

    @method_decorator(require_http_methods(["POST"]))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        get_object_or_404(Proyecto, id=proyecto_id)
        action = request.POST.get("action") or request.headers.get("X-Action", "")

        if action == "recalcular":
            created, updated = recalcular_resumenes(proyecto_id)
            return HttpResponse(
                json.dumps(
                    {
                        "message": f"Resúmenes recalculados: {created} creados, {updated} actualizados.",
                        "created": created,
                        "updated": updated,
                    }
                ),
                content_type="application/json",
                headers={"HX-Trigger": "resumenes-recalculados"},
            )

        return HttpResponseBadRequest(json.dumps({"error": "Acción no válida"}))
