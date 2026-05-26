from apps.red_vial.models.red_vial import Arco
from apps.red_vial.forms.forms import ArcoForm
from apps.red_vial.services.base_service import (
    apply_sort_to_queryset,
    create_item,
    update_item,
    delete_item,
    bulk_update_items,
)


def get_arcos_by_proyecto(proyecto_id, sort_by=None, order='asc'):
    """Retorna arcos de un proyecto con soporte de ordenamiento."""
    qs = Arco.objects.filter(proyecto__id=proyecto_id).select_related('nodo_origen', 'nodo_destino')

    valid_fields = {
        'codigo_arco': ['nodo_origen__numero', 'nodo_destino__numero'],
        'origen': 'nodo_origen__numero',
        'destino': 'nodo_destino__numero',
        'longitud': 'longitud',
    }

    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_arco(proyecto, data):
    """Crea un Arco validando con `ArcoForm` y asignando el proyecto."""
    return create_item(Arco, data, form_class=ArcoForm, proyecto=proyecto)


def update_arco(arco_id, data):
    """Actualiza un Arco usando `ArcoForm` si está disponible."""
    print(f"Updating Arco ID {arco_id} with data: {data}")
    return update_item(Arco, arco_id, data, form_class=ArcoForm)


def delete_arco(arco_id):
    return delete_item(Arco, arco_id)


def bulk_update_arcos(items_data):
    """Actualiza múltiples arcos en lote."""
    fields = ['longitud']
    return bulk_update_items(Arco, items_data, fields)
