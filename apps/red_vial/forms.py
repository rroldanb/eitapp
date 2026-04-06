from django import forms
from apps.red_vial.models import (
    Calle,
    Nodo,
    Arco,
    Movimiento,
    NodoMovimiento,
    Coeficiente_Cruce,
)


class CalleForm(forms.ModelForm):
    """Formulario para crear/editar calles"""

    class Meta:
        model = Calle
        fields = ['numero', 'nombre', 'proyecto']
        widgets = {
            'numero': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Av. Huasco'
            }),
            'proyecto': forms.HiddenInput(),
        }
        labels = {
            'numero': 'Número de Calle',
            'nombre': 'Nombre de la Calle',
        }


class NodoForm(forms.ModelForm):
    """Formulario para crear/editar nodos"""

    class Meta:
        model = Nodo
        fields = ['numero', 'interseccion', 'calle_1', 'calle_2', 'plano', 'imagen', 'proyecto']
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
            'plano': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL del plano'
            }),
            'imagen': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la imagen'
            }),
            'proyecto': forms.HiddenInput(),
        }
        labels = {
            'numero': 'Número del Nodo',
            'interseccion': 'Descripción de la Intersección',
            'calle_1': 'Calle 1',
            'calle_2': 'Calle 2',
            'plano': 'URL del Plano',
            'imagen': 'URL de la Imagen',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            self.fields['calle_1'].queryset = proyecto.calles.all()
            self.fields['calle_2'].queryset = proyecto.calles.all()


class ArcoForm(forms.ModelForm):
    """Formulario para crear/editar arcos"""

    class Meta:
        model = Arco
        fields = ['nodo_origen', 'nodo_destino', 'longitud', 'proyecto']
        widgets = {
            'nodo_origen': forms.Select(attrs={'class': 'form-control'}),
            'nodo_destino': forms.Select(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 150.5',
                'step': '0.01'
            }),
            'proyecto': forms.HiddenInput(),
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


class MovimientoForm(forms.ModelForm):
    """Formulario para crear/editar tipos de movimiento"""

    class Meta:
        model = Movimiento
        fields = ['codigo', 'nombre', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: DIR',
                'maxlength': '2'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Directo'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Movimiento directo'
            }),
        }
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre del Movimiento',
            'descripcion': 'Descripción',
        }


class NodoMovimientoForm(forms.ModelForm):
    """Formulario para crear/editar configuraciones nodo-movimiento"""

    class Meta:
        model = NodoMovimiento
        fields = [
            'nodo', 'movimiento', 'arco_entrada', 'arco_salida',
            'tipo_prioridad', 'regulacion', 'interseccion_valor',
            'numero_pistas', 'velocidad_inicial', 'flujo_total',
            'velocidad_modelo', 'flujo', 'proyecto'
        ]
        widgets = {
            'nodo': forms.Select(attrs={'class': 'form-control'}),
            'movimiento': forms.Select(attrs={'class': 'form-control'}),
            'arco_entrada': forms.Select(attrs={'class': 'form-control'}),
            'arco_salida': forms.Select(attrs={'class': 'form-control'}),
            'tipo_prioridad': forms.Select(attrs={'class': 'form-control'}),
            'regulacion': forms.Select(attrs={'class': 'form-control'}),
            'interseccion_valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'numero_pistas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5'
            }),
            'velocidad_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'flujo_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'velocidad_modelo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'flujo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vehículos/hora'
            }),
            'proyecto': forms.HiddenInput(),
        }
        labels = {
            'nodo': 'Nodo',
            'movimiento': 'Movimiento',
            'arco_entrada': 'Arco de Entrada',
            'arco_salida': 'Arco de Salida',
            'tipo_prioridad': 'Tipo de Prioridad',
            'regulacion': 'Regulación',
            'interseccion_valor': 'Valor de Intersección',
            'numero_pistas': 'Número de Pistas',
            'velocidad_inicial': 'Velocidad Inicial (km/h)',
            'flujo_total': 'Flujo Total',
            'velocidad_modelo': 'Velocidad Modelo (km/h)',
            'flujo': 'Flujo (veh/h)',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            self.fields['nodo'].queryset = proyecto.nodos.all()
            self.fields['arco_entrada'].queryset = proyecto.arcos.all()
            self.fields['arco_salida'].queryset = proyecto.arcos.all()


class CoeficienteCruceForm(forms.ModelForm):
    """Formulario para crear/editar coeficientes de cruce"""

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
