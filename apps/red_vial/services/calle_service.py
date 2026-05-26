from django.db.models import Count, F

from apps.red_vial.models import Calle
from apps.red_vial.forms.forms import CalleForm
from .base_service import apply_sort_to_queryset, create_item, update_item, delete_item, bulk_update_items


# ========== CALLE VIEWS ==========

def get_calles_by_proyecto(proyecto_id, sort_by=None, order='asc'):
    """
    Obtener calles de un proyecto con ordenamiento.
    
    Args:
        proyecto_id: ID del proyecto
        sort_by: Campo para ordenar ('numero', 'nombre', 'nodos')
        order: 'asc' o 'desc'
        
    Returns:
        QuerySet de Calle ordenado
    """
    queryset = Calle.objects.filter(proyecto_id=proyecto_id).annotate(
        nodos_1=Count('nodos_calle_1', distinct=True),
        nodos_2=Count('nodos_calle_2', distinct=True),
    ).annotate(
        nodos_total=F('nodos_1') + F('nodos_2')
    )
    
    valid_sort_fields = {
        'numero': 'numero',
        'nombre': 'nombre',
        'nodos': 'nodos_total',
    }
    
    return apply_sort_to_queryset(
        queryset,
        sort_by=sort_by,
        order=order,
        valid_fields=valid_sort_fields
    )


def create_calle(proyecto, data):
    """Crear una nueva calle."""
    return create_item(Calle, data, form_class=CalleForm, proyecto=proyecto)


def update_calle(calle_id, data):
    """Actualizar una calle."""
    return update_item(Calle, calle_id, data, form_class=CalleForm)


def delete_calle(calle_id):
    """Eliminar una calle."""
    delete_item(Calle, calle_id)


def bulk_update_calles(items_data):
    """Actualizar múltiples calles en lote."""
    return bulk_update_items(Calle, items_data, ['numero', 'nombre'])