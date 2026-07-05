from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from apps.proyectos.models import Proyecto
from apps.red_vial.forms.nodo_form import NodoForm
from apps.red_vial.models import Nodo
from apps.red_vial.services.base_service import (
    apply_sort_to_queryset,
    bulk_update_items,
    delete_item,
    update_item,
)


def get_nodos_by_proyecto(
    proyecto_id: str, sort_by: str | None = None, order: str = "asc"
) -> QuerySet[Nodo]:
    qs = Nodo.objects.filter(proyecto__id=proyecto_id).select_related("calle_1", "calle_2")
    valid_fields = {
        "numero": "numero",
        "calle_1": "calle_1__nombre",
        "calle_2": "calle_2__nombre",
        "is_pc": "is_pc",
        "numero_pc": "numero_pc",
    }
    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_nodo(proyecto: Proyecto, data: dict[str, Any]) -> Nodo:
    form = NodoForm(data, proyecto=proyecto)
    if not form.is_valid():
        raise ValidationError(form.errors)
    nodo = form.save(commit=False)
    nodo.proyecto = proyecto
    nodo.save()
    return nodo


def update_nodo(nodo_id: str, data: dict[str, Any]) -> Nodo:
    return update_item(Nodo, nodo_id, data, form_class=NodoForm)


def delete_nodo(nodo_id: str) -> None:
    return delete_item(Nodo, nodo_id)


def bulk_update_nodos(items_data: list[dict]) -> list[str]:
    fields = ["numero", "is_pc", "numero_pc", "interseccion"]
    return bulk_update_items(Nodo, items_data, fields)


def _update_nodo_file_field(nodo_id: str, file: Any, field: str) -> Nodo:
    from django.shortcuts import get_object_or_404

    from apps.imagenes.services.storage_service import delete_image, upload_image

    nodo = get_object_or_404(Nodo, id=nodo_id)
    old_url = getattr(nodo, field, None)
    if old_url:
        delete_image(old_url)
    setattr(nodo, field, upload_image(file))
    nodo.save()
    return nodo


def _delete_nodo_file_field(nodo_id: str, field: str) -> Nodo:
    from django.shortcuts import get_object_or_404

    from apps.imagenes.services.storage_service import delete_image

    nodo = get_object_or_404(Nodo, id=nodo_id)
    old_url = getattr(nodo, field, None)
    if old_url:
        delete_image(old_url)
    setattr(nodo, field, None)
    nodo.save()
    return nodo


def update_nodo_image(nodo_id: str, file: Any) -> Nodo:
    return _update_nodo_file_field(nodo_id, file, "imagen")


def delete_nodo_image(nodo_id: str) -> Nodo:
    return _delete_nodo_file_field(nodo_id, "imagen")


def update_nodo_plano(nodo_id: str, file: Any) -> Nodo:
    return _update_nodo_file_field(nodo_id, file, "plano")


def delete_nodo_plano(nodo_id: str) -> Nodo:
    return _delete_nodo_file_field(nodo_id, "plano")
