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


def get_detalle_horario(
    proyecto_id: str,
    pc_ids: list[str] | None = None,
    periodo_ids: list[str] | None = None,
    fecha: str | None = None,
    movimiento_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Retorna detalle horario agregando todos los PCs seleccionados.

    Agrupa por (fecha, hora) sumando ftot de todos los PCs, calcula hora
    móvil (rolling 4 intervalos) y etiqueta es_punta según período.
    """
    qs = Periodizacion.objects.filter(pc__proyecto_id=proyecto_id)
    if pc_ids:
        qs = qs.filter(pc_id__in=pc_ids)
    if movimiento_ids:
        qs = qs.filter(pc__movimiento__in=movimiento_ids)
    if fecha:
        qs = qs.filter(fecha=fecha)
    if periodo_ids:
        qs = qs.filter(periodo_id__in=periodo_ids)

    from collections import defaultdict

    # Fetch raw data with periodo info, aggregate by (fecha, hora) in Python
    raw = qs.select_related("periodo").order_by("fecha", "hora", "pc_id")

    groups: dict[tuple, dict] = {}
    for r in raw:
        key = (r.fecha, r.hora)
        if key not in groups:
            groups[key] = {"sum": 0.0, "periodo_codigos": defaultdict(int)}
        groups[key]["sum"] += r.ftot
        cod = r.periodo.codigo if r.periodo else "no"
        if cod in ("PM-L", "PT-L"):
            groups[key]["periodo_codigos"][cod] += 1

    sorted_keys = sorted(groups.keys())

    window: list[float] = []
    all_results: list[dict[str, Any]] = []

    for fecha, hora in sorted_keys:
        g = groups[(fecha, hora)]
        window.append(g["sum"])
        if len(window) > 4:
            window.pop(0)

        hora_movil = round(sum(window), 2) if len(window) == 4 else None

        # es_punta = majority period code among records at this time
        pcodes = g["periodo_codigos"]
        es_punta = max(pcodes, key=pcodes.get) if pcodes else "no"

        all_results.append(
            {
                "fecha": fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha),
                "hora": hora.strftime("%H:%M"),
                "flujo_15min": round(g["sum"], 2),
                "hora_movil": hora_movil,
                "es_punta": es_punta,
            }
        )

    return all_results


def get_detalle_horario_chart_data(
    detalle: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prepara datos JSON para Chart.js combinado bar+line con bandas punta."""
    if not detalle:
        return {"labels": [], "flujo_15min": [], "hora_movil": [], "bandas": []}

    labels = [r["hora"] for r in detalle]
    flujo_data = [r["flujo_15min"] for r in detalle]
    movil_data = [r["hora_movil"] for r in detalle]
    periodos = [r["es_punta"] for r in detalle]

    bandas = []
    current_periodo = None
    band_start = None
    for i, p in enumerate(periodos):
        if p in ("PM-L", "PT-L"):
            if p != current_periodo:
                if band_start is not None:
                    bandas.append(
                        {
                            "from": band_start,
                            "to": i,
                            "label": current_periodo,
                        }
                    )
                band_start = i
                current_periodo = p
        else:
            if band_start is not None:
                bandas.append(
                    {
                        "from": band_start,
                        "to": i,
                        "label": current_periodo,
                    }
                )
                band_start = None
                current_periodo = None

    if band_start is not None:
        bandas.append(
            {
                "from": band_start,
                "to": len(periodos),
                "label": current_periodo,
            }
        )

    return {
        "labels": labels,
        "flujo_15min": flujo_data,
        "hora_movil": movil_data,
        "bandas": bandas,
    }


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


def get_detalle_por_pc_chart_data(
    proyecto_id: str,
    pc_ids: list[str] | None = None,
    periodo_ids: list[str] | None = None,
    fecha: str | None = None,
    movimiento_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Retorna datos de time series (VEQ/15min) agrupados por PC para chart.js.

    Cada PC genera un chart separado con fondo coloreado por periodo punta.
    Si hay múltiples fechas, una línea por fecha.
    """
    qs = Periodizacion.objects.filter(pc__proyecto_id=proyecto_id)
    if pc_ids:
        qs = qs.filter(pc_id__in=pc_ids)
    if movimiento_ids:
        qs = qs.filter(pc__movimiento__in=movimiento_ids)
    if periodo_ids:
        qs = qs.filter(periodo_id__in=periodo_ids)
    if fecha:
        qs = qs.filter(fecha=fecha)

    qs = qs.select_related("pc__nodo", "periodo").order_by("pc_id", "fecha", "hora")

    from collections import OrderedDict, defaultdict

    pc_groups: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for r in qs:
        pc_id = str(r.pc_id)
        if pc_id not in pc_groups:
            nodo = r.pc.nodo
            label = f"PC-{nodo.numero_pc:02d}" if nodo and nodo.numero_pc else r.pc.nombre
            pc_groups[pc_id] = {"label": label, "records": []}
        pc_groups[pc_id]["records"].append(r)

    charts = []
    for pc_id, group in pc_groups.items():
        records = group["records"]
        labels = [r.hora.strftime("%H:%M") for r in records]
        periodos = [
            r.periodo.codigo if r.periodo and r.periodo.codigo in ("PM-L", "PT-L") else "no"
            for r in records
        ]

        # Compute bandas from periodos
        bandas = []
        cur = None
        start = None
        for i, p in enumerate(periodos):
            if p in ("PM-L", "PT-L"):
                if p != cur:
                    if start is not None:
                        bandas.append({"from": start, "to": i, "label": cur})
                    start = i
                    cur = p
            else:
                if start is not None:
                    bandas.append({"from": start, "to": i, "label": cur})
                    start = None
                    cur = None
        if start is not None:
            bandas.append({"from": start, "to": len(periodos), "label": cur})

        # Group by date
        by_date: dict[str, list] = defaultdict(list)
        for r in records:
            by_date[r.fecha.isoformat()].append(r)

        datasets = []
        for i, (date_str, recs) in enumerate(sorted(by_date.items())):
            data = [round(r.ftot, 2) for r in recs]
            bg, border = CHART_COLORS[i % len(CHART_COLORS)]
            datasets.append(
                {
                    "label": date_str,
                    "data": data,
                    "borderColor": border,
                    "backgroundColor": bg,
                    "fill": i == 0,
                    "tension": 0.3,
                    "pointRadius": 2,
                    "pointHoverRadius": 4,
                    "spanGaps": False,
                }
            )

        charts.append(
            {
                "pc_id": pc_id,
                "label": group["label"],
                "labels": labels,
                "datasets": datasets,
                "bandas": bandas,
            }
        )

    return charts
