from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import Count, F, QuerySet

from apps.proyectos.models import Proyecto
from apps.red_vial.forms.calle_form import CalleForm
from apps.red_vial.models import Calle

from .base_service import apply_sort_to_queryset, delete_item, update_item

# ========== CALLE VIEWS ==========


def get_calles_by_proyecto(
    proyecto_id: str, sort_by: str | None = None, order: str = "asc"
) -> QuerySet[Calle]:
    """
    Obtener calles de un proyecto con ordenamiento.

    Args:
        proyecto_id: ID del proyecto
        sort_by: Campo para ordenar ('numero', 'nombre', 'nodos')
        order: 'asc' o 'desc'

    Returns:
        QuerySet de Calle ordenado
    """
    queryset = (
        Calle.objects.filter(proyecto_id=proyecto_id)
        .annotate(
            nodos_1=Count("nodos_calle_1", distinct=True),
            nodos_2=Count("nodos_calle_2", distinct=True),
        )
        .annotate(nodos_total=F("nodos_1") + F("nodos_2"))
    )

    valid_sort_fields = {
        "numero": "numero",
        "nombre": "nombre",
        "nodos": "nodos_total",
    }

    return apply_sort_to_queryset(
        queryset, sort_by=sort_by, order=order, valid_fields=valid_sort_fields
    )


def create_calle(proyecto: Proyecto, data: dict[str, Any]) -> Calle:
    """Crear una nueva calle."""
    form = CalleForm(data, proyecto=proyecto)
    if not form.is_valid():
        raise ValidationError(form.errors)
    calle = form.save(commit=False)
    calle.proyecto = proyecto
    calle.save()
    return calle


def update_calle(calle_id: str, data: dict[str, Any]) -> Calle:
    """Actualizar una calle."""
    return update_item(Calle, calle_id, data, form_class=CalleForm)


def delete_calle(calle_id: str) -> None:
    """Eliminar una calle."""
    delete_item(Calle, calle_id)
