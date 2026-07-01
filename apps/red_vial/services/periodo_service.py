from typing import Any
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.red_vial.models import Periodo
from apps.proyectos.models import Proyecto
from apps.red_vial.forms.periodo_form import PeriodoForm
from .base_service import apply_sort_to_queryset, update_item, delete_item


def get_periodos_by_proyecto(proyecto_id: str, sort_by: str | None = None, order: str = 'asc') -> QuerySet[Periodo]:
    qs = Periodo.objects.filter(proyecto_id=proyecto_id)
    valid_fields = {
        'codigo': 'codigo',
        'hora_inicio': 'hora_inicio',
        'hora_fin': 'hora_fin',
        'es_laboral': 'es_laboral',
    }
    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_periodo(proyecto: Proyecto, data: dict[str, Any]) -> Periodo:
    form = PeriodoForm(data, proyecto=proyecto)
    if not form.is_valid():
        raise ValidationError(form.errors)
    return form.save()


def update_periodo(periodo_id: str, data: dict[str, Any]) -> Periodo:
    return update_item(Periodo, periodo_id, data, form_class=PeriodoForm)


def delete_periodo(periodo_id: str) -> None:
    delete_item(Periodo, periodo_id)
