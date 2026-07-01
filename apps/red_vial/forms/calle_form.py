from django import forms
from django.core.exceptions import ValidationError

from apps.red_vial.models import Calle


class CalleForm(forms.ModelForm):
    class Meta:
        model = Calle
        fields = ['numero', 'nombre']
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Av. Huasco'
            }),
        }
        labels = {
            'numero': 'Número de Calle',
            'nombre': 'Nombre de la Calle',
        }

    def __init__(self, *args, **kwargs):
        self.proyecto = kwargs.pop('proyecto', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get('numero')
        proyecto = self.proyecto or getattr(self.instance, 'proyecto', None)
        if numero and proyecto:
            qs = Calle.objects.filter(numero=numero, proyecto=proyecto)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = f'Ya existe una calle con el número {numero} en este proyecto.'
                raise ValidationError({'numero': msg})
        return cleaned_data
