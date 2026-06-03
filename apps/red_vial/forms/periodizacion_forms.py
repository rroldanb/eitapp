from django import forms
from apps.red_vial.models import Periodizacion

_input = 'w-14 px-1 py-0.5 border border-gray-300 rounded text-center text-xs focus:ring-2 focus:ring-indigo-500 bg-slate-50'

class PeriodizacionForm(forms.ModelForm):
    class Meta:
        model = Periodizacion
        fields = [
            'fecha', 'pc', 'periodo', 'hora',
            'vl', 'txc', 'txb', 'c2e', 'c_mas2e',
            'peat', 'cicl', 'moto',
        ]
        widgets = {
            'vl': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'txc': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'txb': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'c2e': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'c_mas2e': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'peat': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'cicl': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
            'moto': forms.NumberInput(attrs={'class': _input, 'min': '0'}),
        }
        labels = {
            'vl': 'VL', 'txc': 'TXC', 'txb': 'TXB',
            'c2e': 'C 2E', 'c_mas2e': 'C+2E',
            'peat': 'Peat', 'cicl': 'Cicl', 'moto': 'Moto',
        }
