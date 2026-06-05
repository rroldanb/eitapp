from apps.red_vial.models import Nodo
from apps.red_vial.forms.nodo_form import NodoForm
from apps.red_vial.services.base_service import (
    apply_sort_to_queryset,
    create_item,
    update_item,
    delete_item,
    bulk_update_items,
)


def get_nodos_by_proyecto(proyecto_id, sort_by=None, order='asc'):
    """Retorna nodos de un proyecto con soporte de ordenamiento simple."""
    qs = Nodo.objects.filter(proyecto__id=proyecto_id).select_related('calle_1', 'calle_2')

    valid_fields = {
        'numero': 'numero',
        'calle_1': 'calle_1__nombre',
        'calle_2': 'calle_2__nombre',
        'is_pc': 'is_pc',
    }

    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_nodo(proyecto, data):
    """Crea un Nodo validando con `NodoForm` y asignando `proyecto`."""
    # El formulario ya maneja validaciones específicas
    return create_item(Nodo, data, form_class=NodoForm, proyecto=proyecto)


def update_nodo(nodo_id, data):
    """Actualiza un nodo usando `NodoForm` si está disponible."""
    return update_item(Nodo, nodo_id, data, form_class=NodoForm)


def delete_nodo(nodo_id):
    return delete_item(Nodo, nodo_id)


def bulk_update_nodos(items_data):
    # Definir campos que permitimos actualizar en lote
    fields = ['numero', 'is_pc', 'numero_pc', 'interseccion']
    return bulk_update_items(Nodo, items_data, fields)


def _update_nodo_file_field(nodo_id, file, field):
    """Sube un archivo a Supabase y actualiza un campo URL del nodo."""
    from apps.imagenes.services.storage_service import upload_image, delete_image
    nodo = Nodo.objects.get(id=nodo_id)
    old_url = getattr(nodo, field, None)
    if old_url:
        delete_image(old_url)
    setattr(nodo, field, upload_image(file))
    nodo.save()
    return nodo


def _delete_nodo_file_field(nodo_id, field):
    """Elimina un archivo de Supabase y limpia un campo URL del nodo."""
    from apps.imagenes.services.storage_service import delete_image
    nodo = Nodo.objects.get(id=nodo_id)
    old_url = getattr(nodo, field, None)
    if old_url:
        delete_image(old_url)
    setattr(nodo, field, None)
    nodo.save()
    return nodo


def update_nodo_image(nodo_id, file):
    return _update_nodo_file_field(nodo_id, file, 'imagen')


def delete_nodo_image(nodo_id):
    return _delete_nodo_file_field(nodo_id, 'imagen')


def update_nodo_plano(nodo_id, file):
    return _update_nodo_file_field(nodo_id, file, 'plano')


def delete_nodo_plano(nodo_id):
    return _delete_nodo_file_field(nodo_id, 'plano')
