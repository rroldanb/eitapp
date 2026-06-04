from django import forms
from apps.red_vial.models import Arco


class ArcoForm(forms.ModelForm):
    class Meta:
        model = Arco
        fields = ['nodo_origen', 'nodo_destino', 'longitud']
        widgets = {
            'nodo_origen': forms.Select(attrs={'class': 'form-control'}),
            'nodo_destino': forms.Select(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 150.5',
                'step': '0.1'
            }),
        }
        labels = {
            'nodo_origen': 'Nodo de Origen',
            'nodo_destino': 'Nodo de Destino',
            'longitud': 'Longitud (metros)',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            self.fields['nodo_origen'].queryset = proyecto.nodos.all()
            self.fields['nodo_destino'].queryset = proyecto.nodos.all()

    def clean(self):
        cleaned_data = super().clean()
        nodo_origen = cleaned_data.get('nodo_origen')
        nodo_destino = cleaned_data.get('nodo_destino')

        if nodo_origen and nodo_destino and nodo_origen == nodo_destino:
            raise forms.ValidationError('El nodo origen y destino no pueden ser el mismo.')

        return cleaned_data
