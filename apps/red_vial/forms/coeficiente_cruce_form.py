from django import forms
from apps.red_vial.models import Coeficiente_Cruce, CoeficienteCruce


class CoeficienteCruceForm(forms.ModelForm):
    class Meta:
        model = Coeficiente_Cruce
        fields = ['nomenclatura', 'tipo_transporte', 'coeficiente', 'is_standard']
        widgets = {
            'nomenclatura': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: VL'
            }),
            'tipo_transporte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Vehículo Liviano'
            }),
            'coeficiente': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ej: 1.0'
            }),
            'is_standard': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nomenclatura': 'Nomenclatura',
            'tipo_transporte': 'Tipo de Transporte',
            'coeficiente': 'Coeficiente',
            'is_standard': '¿Es estándar?',
        }


class CoeficienteCruceModelForm(forms.ModelForm):
    class Meta:
        model = CoeficienteCruce
        fields = ['nomenclatura', 'tipo_transporte', 'coeficiente', 'is_standard', 'proyecto']
        widgets = {
            'nomenclatura': forms.TextInput(attrs={
                'class': 'w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50',
                'placeholder': 'VL',
            }),
            'tipo_transporte': forms.TextInput(attrs={
                'class': 'px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50',
                'placeholder': 'Vehículo Liviano',
            }),
            'coeficiente': forms.NumberInput(attrs={
                'class': 'w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50',
                'step': '0.01',
                'placeholder': '1.0',
            }),
            'is_standard': forms.CheckboxInput(attrs={'class': 'mr-1'}),
            'proyecto': forms.Select(attrs={
                'class': 'px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50',
            }),
        }
        labels = {
            'nomenclatura': 'Nomenclatura',
            'tipo_transporte': 'Tipo de Transporte',
            'coeficiente': 'Coeficiente',
            'is_standard': '¿Estándar?',
            'proyecto': 'Proyecto',
        }
