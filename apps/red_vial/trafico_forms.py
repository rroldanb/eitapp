from django import forms
from apps.red_vial.models import (
    Periodo,
    ConteoVehicular,
    FlujoMovimiento,
)


class PeriodoForm(forms.ModelForm):
    """Formulario para crear/editar períodos"""

    class Meta:
        model = Periodo
        fields = ['codigo', 'nombre', 'tipo_dia']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: PM-L',
                'maxlength': '10'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Punta Mañana Laboral'
            }),
            'tipo_dia': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'codigo': 'Código del Período',
            'nombre': 'Nombre del Período',
            'tipo_dia': 'Tipo de Día',
        }


class ConteoVehicularForm(forms.ModelForm):
    """Formulario para crear/editar conteos vehiculares"""

    class Meta:
        model = ConteoVehicular
        fields = [
            'nodo', 'periodo', 'hora',
            'vl', 'txc', 'txb', 'c_2e', 'c_mas_2e',
            'peaton', 'ciclista', 'moto',
            
        ]
        widgets = {
            'nodo': forms.Select(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'vl': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vehículos Livianos',
                'step': '0.1'
            }),
            'txc': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Taxi Colectivo',
                'step': '0.1'
            }),
            'txb': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Taxi Básico',
                'step': '0.1'
            }),
            'c_2e': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Camión 2 Ejes',
                'step': '0.1'
            }),
            'c_mas_2e': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Camión +2 Ejes',
                'step': '0.1'
            }),
            'peaton': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Peatones',
                'step': '0.1'
            }),
            'ciclista': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciclistas',
                'step': '0.1'
            }),
            'moto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Motocicletas',
                'step': '0.1'
            }),
            # 'proyecto': forms.HiddenInput(),
        }
        labels = {
            'nodo': 'Nodo',
            'periodo': 'Período',
            'hora': 'Hora',
            'vl': 'Vehículos Livianos (VL)',
            'txc': 'Taxi Colectivo (TXC)',
            'txb': 'Taxi Básico (TXB)',
            'c_2e': 'Camión 2 Ejes (C 2E)',
            'c_mas_2e': 'Camión +2 Ejes (C+2E)',
            'peaton': 'Peatones (Peat)',
            'ciclista': 'Ciclistas (Cicl)',
            'moto': 'Motocicletas (Moto)',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            self.fields['nodo'].queryset = proyecto.nodos.all()


class FlujoMovimientoForm(forms.ModelForm):
    """Formulario para crear/editar flujos de movimiento"""

    class Meta:
        model = FlujoMovimiento
        fields = [
            'nodo_movimiento', 'periodo', 'hora',
            'flujo_veh_hora', 'flujo_veq_15min', 'flujo_veq_hora',
            
        ]
        widgets = {
            'nodo_movimiento': forms.Select(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'flujo_veh_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vehículos por hora',
                'step': '0.01'
            }),
            'flujo_veq_15min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'VEQ / 15 min',
                'step': '0.01'
            }),
            'flujo_veq_hora': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'VEQ / hora',
                'step': '0.01'
            }),
            # 'proyecto': forms.HiddenInput(),
        }
        labels = {
            'nodo_movimiento': 'Nodo-Movimiento',
            'periodo': 'Período',
            'hora': 'Hora',
            'flujo_veh_hora': 'Flujo (veh/h)',
            'flujo_veq_15min': 'Flujo (VEQ/15min)',
            'flujo_veq_hora': 'Flujo (VEQ/h)',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            from apps.red_vial.models import NodoMovimiento
            self.fields['nodo_movimiento'].queryset = NodoMovimiento.objects.filter(proyecto=proyecto)
