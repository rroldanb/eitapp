from typing import Any
from django.db.models import QuerySet

from apps.proyectos.models import Proyecto
from apps.red_vial.models import Arco
from apps.red_vial.forms.arco_form import ArcoForm
from apps.red_vial.services.base_service import (
    apply_sort_to_queryset,
    create_item,
    update_item,
    delete_item,
)


def get_arcos_by_proyecto(proyecto_id: str, sort_by: str | None = None, order: str = 'asc') -> QuerySet[Arco]:
    """Retorna arcos de un proyecto con soporte de ordenamiento."""
    qs = Arco.objects.filter(proyecto__id=proyecto_id).select_related('nodo_origen', 'nodo_destino')

    valid_fields = {
        'codigo_arco': ['nodo_origen__numero', 'nodo_destino__numero'],
        'origen': 'nodo_origen__numero',
        'destino': 'nodo_destino__numero',
        'longitud': 'longitud',
    }

    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_arco(proyecto: Proyecto, data: dict[str, Any]) -> Arco:
    """Crea un Arco validando con `ArcoForm` y asignando el proyecto."""
    return create_item(Arco, data, form_class=ArcoForm, proyecto=proyecto)


def update_arco(arco_id: str, data: dict[str, Any]) -> Arco:
    """Actualiza un Arco usando `ArcoForm` si está disponible."""
    return update_item(Arco, arco_id, data, form_class=ArcoForm)


def delete_arco(arco_id: str) -> None:
    return delete_item(Arco, arco_id)

