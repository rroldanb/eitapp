"""
Base service module para operaciones CRUD genéricas con soporte para ordenamiento.
Proporciona funciones reutilizables para listar, crear, actualizar y eliminar items.
"""
from django.db import transaction
from django.db.models import QuerySet, F
from django.core.exceptions import ValidationError


# ========== FUNCIONES GENÉRICAS DE SORT ==========

def apply_sort_to_queryset(queryset, sort_by=None, order='asc', valid_fields=None, count_annotations=None):
    """
    Aplica ordenamiento a un queryset con validaciones y anotaciones opcionales.
    
    Args:
        queryset: Django QuerySet
        sort_by: Campo para ordenar (str)
        order: 'asc' o 'desc'
        valid_fields: Dict {campo_alias: campo_real} ej: {'nodos': 'nodos_total'}
        count_annotations: Dict de anotaciones de Count/agregación
        
    Returns:
        QuerySet ordenado
    """
    # Aplicar anotaciones si existen
    if count_annotations:
        queryset = queryset.annotate(**count_annotations)
    
    # Validar sort_by
    if valid_fields and sort_by:
        sort_field = valid_fields.get(sort_by)
        if not sort_field:
            sort_field = valid_fields.get(list(valid_fields.keys())[0])
    else:
        sort_field = sort_by or 'id'

    # Validar order
    if order not in ['asc', 'desc']:
        order = 'asc'

    # Aplicar ordenamiento
    if isinstance(sort_field, list):
        if order == 'desc':
            sort_field = [f'-{f}' for f in sort_field]
    else:
        if order == 'desc':
            sort_field = f'-{sort_field}'
        return queryset.order_by(sort_field)
    return queryset.order_by(*sort_field)


def apply_multi_sort_to_queryset(queryset, sort_specs=None, valid_fields=None, count_annotations=None):
    """
    Aplica ordenamiento multi-campo con direcciones independientes.

    Args:
        queryset: Django QuerySet
        sort_specs: Lista de dicts [{'field': 'pc', 'order': 'asc'}, {'field': 'hora', 'order': 'desc'}]
        valid_fields: Dict {campo_alias: campo_real} ej: {'pc': 'pc__nodo__numero_pc'}
        count_annotations: Dict de anotaciones de Count/agregación

    Returns:
        QuerySet ordenado
    """
    if count_annotations:
        queryset = queryset.annotate(**count_annotations)

    if not sort_specs:
        return queryset

    order_fields = []
    for spec in sort_specs:
        alias = spec.get('field')
        direction = spec.get('order', 'asc')

        if valid_fields and alias:
            db_field = valid_fields.get(alias, alias)
        else:
            db_field = alias or 'id'

        if direction == 'desc':
            db_field = f'-{db_field}'
        order_fields.append(db_field)

    return queryset.order_by(*order_fields)


# ========== FUNCIONES GENÉRICAS CRUD ==========

def list_items(queryset):
    """Retorna todos los items del queryset."""
    return queryset.all()


def get_item_by_id(model, item_id):
    """Obtiene un item por ID."""
    return model.objects.get(id=item_id)


def create_item(model, data, form_class=None, **extra_fields):
    """
    Crea un nuevo item.
    
    Args:
        model: Modelo Django
        data: Dict con datos del item
        form_class: Formulario para validación (opcional)
        **extra_fields: Campos adicionales (ej: proyecto=proyecto_obj)
        
    Returns:
        Instancia del modelo creada
    """
    if form_class:
        form = form_class(data)
        if not form.is_valid():
            raise ValidationError(form.errors)
        item = form.save(commit=False)
    else:
        item = model(**data)
    
    # Asignar campos extras
    for key, value in extra_fields.items():
        setattr(item, key, value)
    
    item.save()
    return item


def update_item(model, item_id, data, form_class=None):
    """
    Actualiza un item existente.
    
    Args:
        model: Modelo Django
        item_id: ID del item
        data: Dict con datos a actualizar
        form_class: Formulario para validación (opcional)
        
    Returns:
        Instancia actualizada
    """
    item = get_item_by_id(model, item_id)
    
    if form_class:
        form = form_class(data, instance=item)
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.save()
    else:
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        item.save()
        return item


def delete_item(model, item_id):
    """Elimina un item."""
    item = get_item_by_id(model, item_id)
#    print(f"Eliminando item: {item} (ID: {item.id})")  # Debug log
    item.delete()


def bulk_update_items(model, items_data, fields_to_update):
    """
    Actualiza múltiples items en lote.
    
    Args:
        model: Modelo Django
        items_data: Lista de dicts {id, field1, field2, ...}
        fields_to_update: Lista de campos a actualizar
        
    Returns:
        Lista de IDs actualizados
    """
    updated_ids = []
    updated_items = []
    
    # Obtener IDs y buscar items
    item_ids = [item.get('id') for item in items_data if item.get('id')]
    items_dict = {str(item.id): item for item in model.objects.filter(id__in=item_ids)}
    
    # Actualizar en lote
    with transaction.atomic():
        for item_data in items_data:
            item_id = str(item_data.get('id'))
            item = items_dict.get(item_id)
            
            if not item:
                continue
            
            # Actualizar solo campos permitidos
            for field in fields_to_update:
                if field in item_data:
                    setattr(item, field, item_data[field])
            
            updated_items.append(item)
            updated_ids.append(item_id)
        
        # Bulk update
        if updated_items:
            model.objects.bulk_update(updated_items, fields_to_update)
    
    return updated_ids


# ========== UTILIDADES ==========

def get_or_raise(model, item_id, error_msg="Item not found"):
    """Obtiene un item o lanza una excepción."""
    try:
        return get_item_by_id(model, item_id)
    except model.DoesNotExist:
        raise ValidationError(error_msg)
