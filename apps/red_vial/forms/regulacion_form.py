from django import forms
from apps.red_vial.models import Regulacion


class RegulacionForm(forms.ModelForm):
    class Meta:
        model = Regulacion
        fields = ['codigo', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control bg-slate-50',
                'placeholder': 'Ej: DIR',
                'maxlength': '3'
            }),

            'descripcion': forms.TextInput(attrs={
                'class': 'form-control bg-slate-50',
                'placeholder': 'Ej: Movimiento directo'
            }),
        }
        labels = {
            'codigo': 'Código',
            'descripcion': 'Descripción',
        }
