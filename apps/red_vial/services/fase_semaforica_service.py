from typing import Any
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.red_vial.models.transyt import FaseSemaforica
from apps.proyectos.models import Proyecto
from apps.red_vial.forms.transyt_forms import FaseSemaforicaForm
from .base_service import apply_sort_to_queryset, update_item, delete_item


def get_fases_by_proyecto(proyecto_id: str, sort_by: str | None = None, order: str = 'asc') -> QuerySet[FaseSemaforica]:
    qs = FaseSemaforica.objects.filter(proyecto_id=proyecto_id).select_related(
        'punto_control__nodo'
    )
    valid_fields = {
        'punto_control__nodo__numero_pc': 'punto_control__nodo__numero_pc',
        'punto_control__movimiento': 'punto_control__movimiento',
        'fase_numero': 'fase_numero',
        'verde_inicio': 'verde_inicio',
        'verde_fin': 'verde_fin',
    }
    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_fase_semaforica(proyecto: Proyecto, data: dict[str, Any]) -> FaseSemaforica:
    form = FaseSemaforicaForm(data, proyecto=proyecto)
    if not form.is_valid():
        raise ValidationError(form.errors)
    return form.save()


def update_fase_semaforica(item_id: str, data: dict[str, Any]) -> FaseSemaforica:
    return update_item(FaseSemaforica, item_id, data, form_class=FaseSemaforicaForm)


def delete_fase_semaforica(item_id: str) -> None:
    delete_item(FaseSemaforica, item_id)
