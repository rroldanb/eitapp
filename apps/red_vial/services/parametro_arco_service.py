from typing import Any
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.red_vial.models.transyt import ParametroArco
from apps.proyectos.models import Proyecto
from apps.red_vial.forms.transyt_forms import ParametroArcoForm
from .base_service import apply_sort_to_queryset, update_item, delete_item


def get_parametros_by_proyecto(proyecto_id: str, sort_by: str | None = None, order: str = 'asc') -> QuerySet[ParametroArco]:
    qs = ParametroArco.objects.filter(proyecto_id=proyecto_id).select_related(
        'punto_control__nodo'
    )
    valid_fields = {
        'punto_control__nodo__numero_pc': 'punto_control__nodo__numero_pc',
        'punto_control__movimiento': 'punto_control__movimiento',
        'flujo_saturacion': 'flujo_saturacion',
        'ponderador_demora': 'ponderador_demora',
        'ponderador_detencion': 'ponderador_detencion',
        'capacidad_cola': 'capacidad_cola',
        'tiene_tarjeta_38': 'tiene_tarjeta_38',
    }
    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_parametro_arco(proyecto: Proyecto, data: dict[str, Any]) -> ParametroArco:
    form = ParametroArcoForm(data, proyecto=proyecto)
    if not form.is_valid():
        raise ValidationError(form.errors)
    return form.save()


def update_parametro_arco(item_id: str, data: dict[str, Any]) -> ParametroArco:
    return update_item(ParametroArco, item_id, data, form_class=ParametroArcoForm)


def delete_parametro_arco(item_id: str) -> None:
    delete_item(ParametroArco, item_id)
