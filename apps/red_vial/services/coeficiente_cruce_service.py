from django.db.models import Value
from django.db.models.functions import Coalesce

from apps.red_vial.models import CoeficienteCruce
from apps.red_vial.forms.coeficiente_cruce_form import CoeficienteCruceModelForm
from .base_service import apply_sort_to_queryset, create_item, update_item, delete_item


def get_all_coeficientes_cruce(sort_by=None, order='asc'):
    qs = CoeficienteCruce.objects.select_related('proyecto').all()
    qs = qs.annotate(
        proyecto_sort=Coalesce('proyecto__title', Value(''))
    )
    valid_fields = {
        'nomenclatura': 'nomenclatura',
        'tipo_transporte': 'tipo_transporte',
        'coeficiente': 'coeficiente',
        'proyecto': 'proyecto_sort',
    }
    return apply_sort_to_queryset(qs, sort_by=sort_by, order=order, valid_fields=valid_fields)


def create_coeficiente_cruce(data):
    return create_item(CoeficienteCruce, data, form_class=CoeficienteCruceModelForm)


def update_coeficiente_cruce(item_id, data):
    return update_item(CoeficienteCruce, item_id, data, form_class=CoeficienteCruceModelForm)


def delete_coeficiente_cruce(item_id):
    delete_item(CoeficienteCruce, item_id)
