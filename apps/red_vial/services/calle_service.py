from django.db import transaction
from django.db.models import Count, F
from django.core.exceptions import ValidationError

from apps.red_vial.models import Calle
from apps.red_vial.forms.forms import CalleForm


def get_all_calles():
    """Obtener todas las calles."""
    return Calle.objects.all()


def get_calles_by_proyecto(proyecto_id, sort_by=None, order='asc'):
    """Obtener calles de un proyecto con orden opcional."""
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
    sort_field = valid_sort_fields.get(sort_by, 'numero')
    if order not in ['asc', 'desc']:
        order = 'asc'

    if order == 'desc':
        sort_field = f'-{sort_field}'

    return queryset.order_by(sort_field)


def get_calle_by_id(calle_id):
    """Obtener calle por ID."""
    return Calle.objects.get(id=calle_id)


def _validate_calle_form(data, instance=None):
    """Validar datos de calle con el formulario."""
    form = CalleForm(data, instance=instance)
    if not form.is_valid():
        raise ValidationError(form.errors)
    return form


def create_calle(proyecto, data):
    """Crear una nueva calle vinculada a un proyecto."""
    form = _validate_calle_form(data)
    calle = form.save(commit=False)
    calle.proyecto = proyecto
    calle.save()
    return calle


def update_calle(calle, data):
    """Actualizar una calle existente."""
    form = _validate_calle_form(data, instance=calle)
    return form.save()


def delete_calle(calle_id):
    """Eliminar una calle."""
    calle = Calle.objects.get(id=calle_id)
    calle.delete()


def bulk_update_calles(data_list):
    """Actualizar múltiples calles en lote."""
    updated = []
    updated_ids = []

    calle_ids = [item.get('id') for item in data_list if item.get('id')]
    calles = {str(c.id): c for c in Calle.objects.filter(id__in=calle_ids)}

    with transaction.atomic():
        for item in data_list:
            calle_id = str(item.get('id'))
            calle = calles.get(calle_id)
            if not calle:
                continue

            if 'numero' in item:
                calle.numero = item['numero']
            if 'nombre' in item:
                calle.nombre = item['nombre']

            updated.append(calle)
            updated_ids.append(calle_id)

        if updated:
            Calle.objects.bulk_update(updated, ['numero', 'nombre'])

    return updated_ids