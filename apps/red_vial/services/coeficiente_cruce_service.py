from django.core.exceptions import ValidationError

from apps.red_vial.models import CoeficienteCruce
from apps.red_vial.forms.forms import CoeficienteCruceModelForm


def get_all_coeficientes_cruce():
    return CoeficienteCruce.objects.select_related('proyecto').all()


def create_coeficiente_cruce(data):
    form = CoeficienteCruceModelForm(data)
    if form.is_valid():
        return form.save()
    raise ValidationError(form.errors)


def update_coeficiente_cruce(item_id, data):
    item = CoeficienteCruce.objects.get(id=item_id)
    form = CoeficienteCruceModelForm(data, instance=item)
    if form.is_valid():
        return form.save()
    raise ValidationError(form.errors)


def delete_coeficiente_cruce(item_id):
    CoeficienteCruce.objects.get(id=item_id).delete()
