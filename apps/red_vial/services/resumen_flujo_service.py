from typing import Any

from django.db.models import Avg, Count, Sum

from apps.red_vial.models import Periodizacion, Periodo, PuntoControl, ResumenFlujo

CHART_COLORS = [
    ("rgba(99, 102, 241, 0.6)", "rgba(99, 102, 241, 1)"),
    ("rgba(239, 68, 68, 0.6)", "rgba(239, 68, 68, 1)"),
    ("rgba(16, 185, 129, 0.6)", "rgba(16, 185, 129, 1)"),
    ("rgba(245, 158, 11, 0.6)", "rgba(245, 158, 11, 1)"),
    ("rgba(139, 92, 246, 0.6)", "rgba(139, 92, 246, 1)"),
    ("rgba(14, 165, 233, 0.6)", "rgba(14, 165, 233, 1)"),
    ("rgba(236, 72, 153, 0.6)", "rgba(236, 72, 153, 1)"),
    ("rgba(34, 197, 94, 0.6)", "rgba(34, 197, 94, 1)"),
]


def recalcular_resumenes(proyecto_id: str) -> dict[str, int]:
    """Recalcula ResumenFlujo para todos los PCs y Periodos del proyecto desde Periodización."""
    aggs = (
        Periodizacion.objects.filter(pc__proyecto_id=proyecto_id)
        .values("pc", "periodo")
        .annotate(
            flujo_total=Sum("ftot"),
            promedio=Avg("ftot"),
            num_registros=Count("id"),
        )
    )

    created_count = 0
    updated_count = 0
    for agg in aggs:
        flujo = max(10, round(agg["flujo_total"] or 0))
        _obj, created = ResumenFlujo.objects.update_or_create(
            pc_id=agg["pc"],
            periodo_id=agg["periodo"],
            defaults={
                "flujo_total": round(agg["flujo_total"], 2) if agg["flujo_total"] else 0,
                "promedio": round(agg["promedio"], 2) if agg["promedio"] else 0,
                "num_registros": agg["num_registros"],
                "flujo": flujo,
            },
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
    return created_count, updated_count


def get_analisis_flujos(
    proyecto_id: str,
    pc_ids: list[str] | None = None,
    periodo_ids: list[str] | None = None,
    fecha: str | None = None,
) -> list[dict[str, Any]]:
    """Retorna datos agregados para el dashboard de Análisis de Flujos."""
    if fecha:
        qs = Periodizacion.objects.filter(pc__proyecto_id=proyecto_id, fecha=fecha)
        if pc_ids:
            qs = qs.filter(pc_id__in=pc_ids)
        if periodo_ids:
            qs = qs.filter(periodo_id__in=periodo_ids)

        rows = qs.values("pc", "periodo").annotate(
            flujo_total=Sum("ftot"),
            promedio=Avg("ftot"),
            num_registros=Count("id"),
        )
    else:
        qs = ResumenFlujo.objects.filter(pc__proyecto_id=proyecto_id)
        if pc_ids:
            qs = qs.filter(pc_id__in=pc_ids)
        if periodo_ids:
            qs = qs.filter(periodo_id__in=periodo_ids)

        rows = qs.values("pc", "periodo", "flujo_total", "promedio", "num_registros")

    # Enrich with related objects
    pc_ids_set = set(r["pc"] for r in rows)
    periodo_ids_set = set(r["periodo"] for r in rows)

    pcs = {
        str(p.id): p for p in PuntoControl.objects.filter(id__in=pc_ids_set).select_related("nodo")
    }
    periodos = {str(p.id): p for p in Periodo.objects.filter(id__in=periodo_ids_set)}

    enriched = []
    for r in rows:
        pc = pcs.get(str(r["pc"]))
        per = periodos.get(str(r["periodo"]))
        enriched.append(
            {
                "pc_id": r["pc"],
                "pc_nombre": pc.nombre if pc else "—",
                "pc_numero": pc.nodo.numero_pc if pc and pc.nodo else None,
                "movimiento": pc.get_movimiento_display() if pc else "—",
                "periodo_id": r["periodo"],
                "periodo_codigo": per.codigo if per else "—",
                "periodo_nombre": per.get_codigo_display() if per else "—",
                "flujo_total": round(r.get("flujo_total", 0) or 0, 2),
                "promedio": round(r.get("promedio", 0) or 0, 2),
                "num_registros": r.get("num_registros", 0) or 0,
            }
        )

    return enriched


def get_ranking(analisis_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Agrupa por PC y ordena por flujo_total descendente."""
    ranking_map = {}
    for item in analisis_data:
        pc_id = item["pc_id"]
        if pc_id not in ranking_map:
            ranking_map[pc_id] = {
                "pc_id": pc_id,
                "pc_nombre": item["pc_nombre"],
                "pc_numero": item["pc_numero"],
                "movimiento": item["movimiento"],
                "total_flujo": 0,
            }
        ranking_map[pc_id]["total_flujo"] += item["flujo_total"]

    ranking = sorted(ranking_map.values(), key=lambda x: x["total_flujo"], reverse=True)
    for i, r in enumerate(ranking, 1):
        r["rank"] = i
    return ranking


def get_comparison(
    analisis_data: list[dict[str, Any]], periodos_ordered: list[Periodo]
) -> dict[str, Any]:
    """Estructura datos para comparación por periodo (pivot)."""
    from collections import OrderedDict

    comparison_map = OrderedDict()
    for item in analisis_data:
        pc_id = item["pc_id"]
        if pc_id not in comparison_map:
            comparison_map[pc_id] = {
                "pc_nombre": item["pc_nombre"],
                "pc_numero": item["pc_numero"],
                "movimiento": item["movimiento"],
                "valores": {},
            }
        comparison_map[pc_id]["valores"][item["periodo_id"]] = item["flujo_total"]

    result = []
    for _pc_id, data in comparison_map.items():
        row = {
            "pc_nombre": data["pc_nombre"],
            "pc_numero": data["pc_numero"],
            "movimiento": data["movimiento"],
        }
        for p in periodos_ordered:
            pid = str(p.id)
            row[pid] = data["valores"].get(pid, 0)
        result.append(row)
    return result


def get_chart_data(
    analisis_data: list[dict[str, Any]], periodos_ordered: list[Periodo]
) -> dict[str, Any]:
    """Prepara datos JSON para Chart.js."""
    from collections import OrderedDict

    chart_map = OrderedDict()
    periodo_labels = []

    for item in analisis_data:
        pc_label = f"PC-{item['pc_numero']:02d}" if item["pc_numero"] else item["pc_nombre"]
        if pc_label not in chart_map:
            chart_map[pc_label] = {}
        chart_map[pc_label][item["periodo_id"]] = item["flujo_total"]

    for p in periodos_ordered:
        pid = str(p.id)
        periodo_labels.append(f"{p.codigo}")

    labels = list(chart_map.keys())
    datasets = []
    for idx, p in enumerate(periodos_ordered):
        pid = str(p.id)
        data = [chart_map[lbl].get(pid, 0) for lbl in labels]
        bg, border = CHART_COLORS[idx % len(CHART_COLORS)]
        datasets.append(
            {
                "label": p.codigo,
                "data": data,
                "backgroundColor": bg,
                "borderColor": border,
                "borderWidth": 1,
            }
        )

    return {"labels": labels, "datasets": datasets}
