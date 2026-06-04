from django import forms
from apps.red_vial.models import Nodo


class NodoForm(forms.ModelForm):
    class Meta:
        model = Nodo
        fields = ['numero', 'interseccion', 'calle_1', 'calle_2', 'plano', 'imagen',  'numero_pc']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PC 01'
            }),
            'interseccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Av. Huasco con Armando Rossel'
            }),
            'calle_1': forms.Select(attrs={'class': 'form-control'}),
            'calle_2': forms.Select(attrs={'class': 'form-control'}),
            'numero_pc': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de PC (si aplica)'
            }),
            'plano': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL del plano'
            }),
            'imagen': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la imagen'
            }),
        }
        labels = {
            'numero': 'Número del Nodo',
            'interseccion': 'Descripción de la Intersección',
            'calle_1': 'Calle 1',
            'calle_2': 'Calle 2',
            'numero_pc': 'Número de PC (si es aplicable)',
            'plano': 'URL del Plano',
            'imagen': 'URL de la Imagen',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            self.fields['calle_1'].queryset = proyecto.calles.all()
            self.fields['calle_2'].queryset = proyecto.calles.all()
