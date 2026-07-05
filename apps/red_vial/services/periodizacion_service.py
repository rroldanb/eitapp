from datetime import date, datetime, timedelta
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet

from apps.proyectos.models import Proyecto
from apps.red_vial.models import Periodizacion, Periodo, PuntoControl

from .base_service import (
    apply_multi_sort_to_queryset,
    delete_item,
    get_item_by_id,
)

VALID_SORT_FIELDS = {
    "pc": "pc__nodo__numero_pc",
    "interseccion": "pc__nodo__calle_1__nombre",
    "hora": "hora",
    "mov": "pc__movimiento",
    "periodo": "periodo__codigo",
    "vl": "vl",
    "txc": "txc",
    "txb": "txb",
    "c2e": "c2e",
    "c_mas2e": "c_mas2e",
    "peat": "peat",
    "cicl": "cicl",
    "moto": "moto",
    "ftot": "ftot",
}


def parse_sort_specs(
    sort_param: str | None, order_param: str | None
) -> list[dict[str, str]] | None:
    """
    Parsea parámetros de sort multi-campo.

    sort_param: cadena separada por comas, ej: "pc,-hora,mov"
    order_param: cadena separada por comas, ej: "asc,desc,asc"
    """
    if not sort_param:
        return None

    fields = [f.strip() for f in sort_param.split(",") if f.strip()]
    orders = [o.strip() for o in order_param.split(",")] if order_param else []

    specs = []
    for i, field in enumerate(fields):
        direction = "desc" if field.startswith("-") else (orders[i] if i < len(orders) else "asc")
        clean_field = field.lstrip("-")
        specs.append({"field": clean_field, "order": direction})

    return specs


def get_periodizaciones(
    proyecto_id: str,
    nodo_ids: list[str] | None = None,
    periodo_ids: list[str] | None = None,
    movimiento_ids: list[str] | None = None,
    fecha: date | None = None,
    sort_param: str | None = None,
    order_param: str = "asc",
) -> QuerySet[Periodizacion]:
    """Lista periodizaciones con filtros multi-select y orden anidado."""
    qs = Periodizacion.objects.filter(pc__proyecto_id=proyecto_id)

    if nodo_ids:
        qs = qs.filter(pc__nodo_id__in=nodo_ids)
    if periodo_ids:
        qs = qs.filter(periodo_id__in=periodo_ids)
    if movimiento_ids:
        qs = qs.filter(pc__movimiento__in=movimiento_ids)
    if fecha:
        qs = qs.filter(fecha=fecha)

    qs = qs.select_related(
        "pc__nodo__calle_1",
        "pc__nodo__calle_2",
        "periodo",
    ).order_by("pc__nodo__numero_pc", "hora", "pc__movimiento")

    sort_specs = parse_sort_specs(sort_param, order_param)
    if sort_specs:
        qs = apply_multi_sort_to_queryset(qs, sort_specs, valid_fields=VALID_SORT_FIELDS)

    return qs


@transaction.atomic
def generar_filas(
    proyecto: Proyecto,
    nodo_ids: list[str],
    periodo_ids: list[str],
    fecha: date,
    movimiento_ids: list[str] | None = None,
) -> int:
    """
    Genera filas de 15 min para cada combinación PC (todos sus movimientos) x Periodo.
    No duplica filas existentes (get_or_create).
    """
    filas_creadas = 0
    pcs = PuntoControl.objects.filter(nodo_id__in=nodo_ids, proyecto=proyecto)
    if movimiento_ids:
        pcs = pcs.filter(movimiento__in=movimiento_ids)
    periodos = Periodo.objects.filter(id__in=periodo_ids, proyecto=proyecto)

    for pc in pcs:
        if not pc.arco_salida_id or not pc.arco_entrada_id:
            continue
        pc_mov = f"{pc.arco_salida.codigo_arco}_{pc.arco_entrada.codigo_arco}"
        for periodo in periodos:
            if not periodo.hora_inicio or not periodo.hora_fin:
                continue
            hora_actual = periodo.hora_inicio
            while hora_actual < periodo.hora_fin:
                _, created = Periodizacion.objects.get_or_create(
                    fecha=fecha,
                    pc_mov=pc_mov,
                    hora=hora_actual,
                    defaults={
                        "pc": pc,
                        "periodo": periodo,
                        "vl": 0,
                        "txc": 0,
                        "txb": 0,
                        "c2e": 0,
                        "c_mas2e": 0,
                        "peat": 0,
                        "cicl": 0,
                        "moto": 0,
                    },
                )
                if created:
                    filas_creadas += 1
                # Avanzar 15 minutos
                dt = datetime.combine(date.today(), hora_actual) + timedelta(minutes=15)
                hora_actual = dt.time()
    return filas_creadas


# def update_periodizacion(pc_id, data):
#     """Actualiza un registro de periodización."""
#     return update_item(Periodizacion, pc_id, data, form_class=PeriodizacionForm)

COUNT_FIELDS = {"vl", "txc", "txb", "c2e", "c_mas2e", "peat", "cicl", "moto"}


def update_periodizacion(pc_id: str, data: dict[str, Any]) -> Periodizacion:
    item = get_item_by_id(Periodizacion, pc_id)
    for field in COUNT_FIELDS:
        if field in data:
            try:
                setattr(item, field, int(data[field]))
            except (ValueError, TypeError):
                raise ValidationError({field: "Debe ser un número entero"})
    item.save()
    return item


def delete_periodizacion(pc_id: str) -> None:
    """Elimina un registro de periodización."""
    delete_item(Periodizacion, pc_id)
