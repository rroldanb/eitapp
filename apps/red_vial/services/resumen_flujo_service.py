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
        comparison_map[pc_id]["valores"][str(item["periodo_id"])] = item["flujo_total"]

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
    móvil (rolling 4 intervalos) y etiqueta es_punta por período:
    por cada (período, fecha) se toman los 5 slots consecutivos de mayor
    hora móvil (el pico ±2).
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

    # --- Step 1: aggregate ftot and track which periods are present ---
    groups: dict[tuple, dict] = {}
    for r in raw:
        key = (r.fecha, r.hora)
        if key not in groups:
            groups[key] = {"sum": 0.0, "periodos": set()}
        groups[key]["sum"] += r.ftot
        cod = r.periodo.codigo if r.periodo else "no"
        if cod in ("PM-L", "PT-L"):
            groups[key]["periodos"].add(cod)

    sorted_keys = sorted(groups.keys())

    # --- Step 2: build result rows with flujo_15min (hora_movil assigned later) ---
    all_results: list[dict[str, Any]] = []

    for fecha, hora in sorted_keys:
        g = groups[(fecha, hora)]
        all_results.append(
            {
                "fecha": fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha),
                "hora": hora.strftime("%H:%M"),
                "flujo_15min": round(g["sum"], 2),
                "hora_movil": None,
                "es_punta": "no",
            }
        )

    # Quick lookup: (fecha_str, hora_str) → index in all_results
    result_index: dict[tuple[str, str], int] = {
        (row["fecha"], row["hora"]): i for i, row in enumerate(all_results)
    }

    # --- Step 3: per-period forward-looking rolling window + peak detection ---
    selected_codes = ["PM-L", "PT-L"]
    periodos_map = {
        p.codigo: p
        for p in Periodo.objects.filter(proyecto_id=proyecto_id, codigo__in=selected_codes)
    }

    es_punta_map: dict[tuple[str, str], set[str]] = {}
    # key: (fecha_str, hora_str) → set of period codes marking this slot as peak

    for codigo in selected_codes:
        p = periodos_map.get(codigo)
        if not p or not p.hora_inicio or not p.hora_fin:
            continue

        # Collect (fecha_str, hora_str, flujo) rows within this period's time range
        period_entries: list[tuple[str, str, float]] = []
        for fecha_obj, hora_obj in sorted_keys:
            if not (p.hora_inicio <= hora_obj <= p.hora_fin):
                continue
            if codigo not in groups[(fecha_obj, hora_obj)]["periodos"]:
                continue
            fecha_str = fecha_obj.isoformat() if hasattr(fecha_obj, "isoformat") else str(fecha_obj)
            period_entries.append(
                (fecha_str, hora_obj.strftime("%H:%M"), groups[(fecha_obj, hora_obj)]["sum"])
            )

        # Group by date
        date_data: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for fecha_str, hora_str, flujo in period_entries:
            date_data[fecha_str].append((hora_str, flujo))

        for fecha_str, entries in date_data.items():
            entries.sort(key=lambda x: x[0])
            if len(entries) < 4:
                continue

            # Forward-looking rolling window: current + 3 next
            for i in range(len(entries) - 3):
                hora_str = entries[i][0]
                movil = round(sum(entries[j][1] for j in range(i, i + 4)), 2)

                # Assign per-period hora_movil to result row
                rkey = (fecha_str, hora_str)
                idx = result_index.get(rkey)
                if idx is not None:
                    all_results[idx]["hora_movil"] = movil

            # Find peak (max forward-looking hora_movil within this date+period)
            valid = [
                (i, sum(entries[j][1] for j in range(i, i + 4))) for i in range(len(entries) - 3)
            ]
            if not valid:
                continue
            peak_idx = max(valid, key=lambda x: x[1])[0]

            # Mark ±2 slots as peak for this period
            for offset in range(-2, 3):
                idx = peak_idx + offset
                if 0 <= idx < len(entries):
                    key = (fecha_str, entries[idx][0])
                    if key not in es_punta_map:
                        es_punta_map[key] = set()
                    es_punta_map[key].add(codigo)

    # --- Step 4: assign es_punta from peak map ---
    for row in all_results:
        key = (row["fecha"], row["hora"])
        punta_set = es_punta_map.get(key, set())
        if len(punta_set) > 1:
            row["es_punta"] = "AMBOS"
        elif len(punta_set) == 1:
            row["es_punta"] = punta_set.pop()
        else:
            row["es_punta"] = "no"

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
    """Retorna datos de time series (VEQ/15min) agrupados por nodo para chart.js.

    Cada nodo (intersección) genera UN chart con una línea por movimiento (PC).
    El usuario puede togglear cada movimiento desde el frontend.
    Fondo coloreado por periodo punta (PM-L / PT-L).
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

    qs = qs.select_related("pc__nodo__calle_1", "pc__nodo__calle_2", "periodo").order_by(
        "pc__nodo_id", "pc__movimiento", "fecha", "hora"
    )

    from collections import OrderedDict

    movimiento_choices = dict(PuntoControl.Movimiento.choices)

    # Group by nodo, then sub-group by pc (each PC = one movimiento)
    nodo_groups: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for r in qs:
        nodo_id = str(r.pc.nodo_id)
        if nodo_id not in nodo_groups:
            nodo = r.pc.nodo
            calle_1 = nodo.calle_1.nombre if nodo.calle_1 else ""
            calle_2 = nodo.calle_2.nombre if nodo.calle_2 else ""
            interseccion = f"{calle_1} / {calle_2}".strip(" /")
            label = f"PC-{nodo.numero_pc:02d} - {interseccion}" if nodo.numero_pc else interseccion
            nodo_groups[nodo_id] = {
                "nodo_id": nodo_id,
                "numero_pc": nodo.numero_pc or 999,
                "label": label,
                "pcs": OrderedDict(),
            }
        pc_id = str(r.pc_id)
        if pc_id not in nodo_groups[nodo_id]["pcs"]:
            mov_label = movimiento_choices.get(r.pc.movimiento, r.pc.movimiento)
            nodo_groups[nodo_id]["pcs"][pc_id] = {
                "movimiento_id": r.pc.movimiento,
                "movimiento_label": mov_label,
                "records": [],
            }
        nodo_groups[nodo_id]["pcs"][pc_id]["records"].append(r)

    # Sort nodos by numero_pc
    sorted_groups = sorted(nodo_groups.values(), key=lambda g: g["numero_pc"])

    charts = []
    color_idx = 0
    for group in sorted_groups:
        nodo_id = group["nodo_id"]
        all_records = []
        for _pc_id, pc_data in group["pcs"].items():
            all_records.extend(pc_data["records"])

        if not all_records:
            continue

        # Build time labels from all records, deduplicated and sorted chronologically
        labels = sorted({r.hora.strftime("%H:%M") for r in all_records})

        # Build time→index map
        time_index = {t: i for i, t in enumerate(labels)}

        # Compute bandas from unique time slots (from PC with most records)
        pcs_sorted = sorted(group["pcs"].values(), key=lambda x: len(x["records"]), reverse=True)
        ref_pc = pcs_sorted[0]["records"] if pcs_sorted else []
        slot_map: dict[str, str] = {}
        for r in ref_pc:
            t = r.hora.strftime("%H:%M")
            if t not in slot_map:
                cod = (
                    r.periodo.codigo if r.periodo and r.periodo.codigo in ("PM-L", "PT-L") else "no"
                )
                slot_map[t] = cod
        slot_periodos = [slot_map.get(t, "no") for t in labels]

        bandas = []
        cur = None
        start = None
        for i, p in enumerate(slot_periodos):
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
            bandas.append({"from": start, "to": len(slot_periodos), "label": cur})

        # One dataset per movimiento (PC), aggregated across dates
        movimientos_list = []
        datasets = []
        for _pc_id, pc_data in group["pcs"].items():
            bg, border = CHART_COLORS[color_idx % len(CHART_COLORS)]
            color_idx += 1

            # Initialize data array aligned to labels
            data = [None] * len(labels)
            for r in pc_data["records"]:
                t = r.hora.strftime("%H:%M")
                if t in time_index:
                    idx = time_index[t]
                    if data[idx] is None:
                        data[idx] = 0.0
                    data[idx] += round(r.ftot, 2)

            datasets.append(
                {
                    "label": pc_data["movimiento_label"],
                    "data": data,
                    "borderColor": border,
                    "backgroundColor": bg,
                    "fill": False,
                    "tension": 0.3,
                    "pointRadius": 2,
                    "pointHoverRadius": 4,
                    "spanGaps": False,
                    "movimiento_id": pc_data["movimiento_id"],
                }
            )
            movimientos_list.append(
                {
                    "id": pc_data["movimiento_id"],
                    "label": pc_data["movimiento_label"],
                    "color": border,
                    "visible": True,
                }
            )

        charts.append(
            {
                "nodo_id": nodo_id,
                "label": group["label"],
                "labels": labels,
                "datasets": datasets,
                "movimientos": movimientos_list,
                "bandas": bandas,
            }
        )

    return charts
