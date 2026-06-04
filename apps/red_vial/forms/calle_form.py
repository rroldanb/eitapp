from django import forms
from apps.red_vial.models import Calle


class CalleForm(forms.ModelForm):
    class Meta:
        model = Calle
        fields = ['numero', 'nombre', ]
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
