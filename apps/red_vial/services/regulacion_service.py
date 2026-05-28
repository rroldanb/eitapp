from apps.red_vial.models import Regulacion
from apps.red_vial.forms.forms import RegulacionForm
from .base_service import apply_sort_to_queryset, create_item, update_item, delete_item


def get_all_regulaciones(sort_by=None, order='asc'):
    qs = Regulacion.objects.all()

    valid_fields = {
        'codigo': 'codigo',
        'descripcion': 'descripcion',
    }

    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_regulacion(data):
    return create_item(Regulacion, data, form_class=RegulacionForm)


def update_regulacion(regulacion_id, data):
    return update_item(Regulacion, regulacion_id, data, form_class=RegulacionForm)


def delete_regulacion(regulacion_id):
    delete_item(Regulacion, regulacion_id)
