from typing import Any

from django.db.models import QuerySet

from apps.red_vial.forms.regulacion_form import RegulacionForm
from apps.red_vial.models import Regulacion

from .base_service import apply_sort_to_queryset, create_item, delete_item, update_item


def get_all_regulaciones(sort_by: str | None = None, order: str = "asc") -> QuerySet[Regulacion]:
    qs = Regulacion.objects.all()

    valid_fields = {
        "codigo": "codigo",
        "descripcion": "descripcion",
    }

    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_regulacion(data: dict[str, Any]) -> Regulacion:
    return create_item(Regulacion, data, form_class=RegulacionForm)


def update_regulacion(regulacion_id: str, data: dict[str, Any]) -> Regulacion:
    return update_item(Regulacion, regulacion_id, data, form_class=RegulacionForm)


def delete_regulacion(regulacion_id: str) -> None:
    delete_item(Regulacion, regulacion_id)
