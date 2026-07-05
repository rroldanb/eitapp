from typing import Any

from django.db.models import QuerySet

from apps.proyectos.models import Proyecto
from apps.red_vial.forms.punto_control_form import PuntoControlForm
from apps.red_vial.models import PuntoControl

from .base_service import apply_sort_to_queryset, create_item, delete_item, update_item


def get_puntos_control_by_proyecto(
    proyecto_id: str, sort_by: str | None = None, order: str = "asc"
) -> QuerySet[PuntoControl]:
    queryset = PuntoControl.objects.filter(proyecto_id=proyecto_id).select_related(
        "nodo", "arco_entrada", "arco_salida", "regulacion"
    )

    valid_sort_fields = {
        "nombre": "nodo__numero_pc",
        "nodo": "nodo__numero",
        "movimiento": "movimiento",
        "viraje": "viraje",
        "arco_entrada": "arco_entrada__nodo_origen__numero",
        "arco_salida": "arco_salida__nodo_destino__numero",
        "regulacion": "regulacion__codigo",
        "numero_pistas": "numero_pistas",
    }
    if sort_by:
        return apply_sort_to_queryset(
            queryset, sort_by=sort_by, order=order, valid_fields=valid_sort_fields
        )
    # Default: PC number ASC, movimiento DESC
    return queryset.order_by("nodo__numero_pc", "movimiento")


def create_punto_control(proyecto: Proyecto, data: dict[str, Any]) -> PuntoControl:
    return create_item(PuntoControl, data, form_class=PuntoControlForm, proyecto=proyecto)


def update_punto_control(pc_id: str, data: dict[str, Any]) -> PuntoControl:
    return update_item(PuntoControl, pc_id, data, form_class=PuntoControlForm)


def delete_punto_control(pc_id: str) -> None:
    delete_item(PuntoControl, pc_id)
