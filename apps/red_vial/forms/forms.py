from django import forms
from apps.red_vial.models import (
    Calle,
    Nodo,
    Arco,
    Regulacion,
    NodoMovimiento,
    Coeficiente_Cruce,
    PuntoControl,
    CoeficienteCruce,
)


class CalleForm(forms.ModelForm):
    """Formulario para crear/editar calles"""

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
            # 'proyecto': forms.HiddenInput(),
        }
        labels = {
            'numero': 'Número de Calle',
            'nombre': 'Nombre de la Calle',
        }

class NodoForm(forms.ModelForm):
    """Formulario para crear/editar nodos"""

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
            # 'is_pc': forms.CheckboxInput(attrs={
            #     'class': 'form-check-input'
            # }),
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
            # 'proyecto': forms.HiddenInput(),
        }
        labels = {
            'numero': 'Número del Nodo',
            'interseccion': 'Descripción de la Intersección',
            'calle_1': 'Calle 1',
            'calle_2': 'Calle 2',
            # 'is_pc': '¿Es Punto de Control (PC)?',
            'numero_pc': 'Número de PC (si es aplicable)',
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
        fields = ['nodo_origen', 'nodo_destino', 'longitud']
        widgets = {
            'nodo_origen': forms.Select(attrs={'class': 'form-control'}),
            'nodo_destino': forms.Select(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 150.5',
                'step': '0.1'
            }),
            # 'proyecto': forms.HiddenInput(),
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


class RegulacionForm(forms.ModelForm):
    """Formulario para crear/editar tipos de regulación"""

    class Meta:
        model = Regulacion
        fields = ['codigo', 'descripcion']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: DIR',
                'maxlength': '3'
            }),

            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Movimiento directo'
            }),
        }
        labels = {
            'codigo': 'Código',
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
            'velocidad_modelo', 'flujo', 
        ]
        widgets = {
            'nodo': forms.Select(attrs={'class': 'form-control'}),
            'arco_entrada': forms.Select(attrs={'class': 'form-control'}),
            'arco_salida': forms.Select(attrs={'class': 'form-control'}),
            'tipo_prioridad': forms.Select(attrs={'class': 'form-control'}),
            'movimiento': forms.Select(attrs={'class': 'form-control'}),
            'regulacion': forms.Select(attrs={'class': 'form-control'}),
            'interseccion_valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'numero_pistas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5'
            }),
            'velocidad_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'flujo_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'velocidad_modelo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'flujo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vehículos/hora'
            }),
            # 'proyecto': forms.HiddenInput(),
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


_input = 'w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50'
_select = 'px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50' 

class PuntoControlForm(forms.ModelForm):
    class Meta:
        model = PuntoControl
        fields = [
             'nodo', 'movimiento', 'viraje', 'is_prioritario',
            'arco_entrada', 'arco_salida', 'regulacion', 'numero_pistas',
        ]
        widgets = {
            # 'nombre': forms.TextInput(attrs={
            #     'class': _input,
            #     'placeholder': 'PC-01',
            #     'maxlength': '5',
            # }),
            'nodo': forms.Select(attrs={'class': _select, }),
            'movimiento': forms.Select(attrs={'class': _select, }),
            'viraje': forms.Select(attrs={'class': _select, }),
            'is_prioritario': forms.CheckboxInput(attrs={'class': 'mr-1'}),
            'arco_entrada': forms.Select(attrs={'class': _select, }),
            'arco_salida': forms.Select(attrs={'class': _select, }),
            'regulacion': forms.Select(attrs={'class': _select, }),
            'numero_pistas': forms.NumberInput(attrs={
                'class': _input.replace('w-24', 'w-20'),
                'step': '0.5',
                'placeholder': 'Pistas',
            }),
        }
        labels = {
            # 'nombre': 'Nombre PC',
            'nodo': 'Nodo',
            'movimiento': 'Movimiento',
            'viraje': 'Tipo de Viraje',
            'is_prioritario': '¿Es prioritario?',
            'arco_entrada': 'Arco de Entrada',
            'arco_salida': 'Arco de Salida',
            'regulacion': 'Regulación',
            'numero_pistas': 'Número de Pistas',
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            # self.fields['nodo'].queryset = proyecto.nodos.all()
            self.fields['nodo'].queryset = (
                proyecto.nodos
                .filter(numero_pc__isnull=False)
                .select_related('calle_1', 'calle_2')
                .order_by('numero_pc')
            )
            self.fields['nodo'].label_from_instance = lambda obj: (
                f"{obj.nombre_pc} - "
                f"{obj.calle_1.nombre if obj.calle_1 else 'Sin calle'} / "
                f"{obj.calle_2.nombre if obj.calle_2 else 'Sin intersección'}"
            )
            # self.fields['arco_entrada'].queryset = proyecto.arcos.all().order_by('codigo_arco')
            self.fields['arco_entrada'].queryset = proyecto.arcos.all().order_by('nodo_origen__numero', 'nodo_destino__numero')
            self.fields['arco_salida'].queryset = proyecto.arcos.all().order_by('nodo_origen__numero', 'nodo_destino__numero')
            self.fields['nodo'].empty_label = 'Selecciona un Punto de Control (PC)'
            self.fields['arco_entrada'].empty_label = 'Selecciona un arco de entrada'
            self.fields['arco_salida'].empty_label = 'Selecciona un arco de salida'
            self.fields['regulacion'].empty_label = 'Selecciona una regulación'
            self.fields['movimiento'].choices = [('', 'Selecciona un movimiento')] + [(value, f"{value} - {label}") for value, label in self.fields['movimiento'].choices]
            self.fields['viraje'].choices = [('', 'Selecciona un viraje')] + list(self.fields['viraje'].choices)
            self.fields['numero_pistas'].initial = 1


class CoeficienteCruceModelForm(forms.ModelForm):
    class Meta:
        model = CoeficienteCruce
        fields = ['nomenclatura', 'tipo_transporte', 'coeficiente', 'is_standard', 'proyecto']
        widgets = {
            'nomenclatura': forms.TextInput(attrs={
                'class': 'w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'VL',
            }),
            'tipo_transporte': forms.TextInput(attrs={
                'class': 'px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Vehículo Liviano',
            }),
            'coeficiente': forms.NumberInput(attrs={
                'class': 'w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
                'step': '0.01',
                'placeholder': '1.0',
            }),
            'is_standard': forms.CheckboxInput(attrs={'class': 'mr-1'}),
            'proyecto': forms.Select(attrs={
                'class': 'px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500',
            }),
        }
        labels = {
            'nomenclatura': 'Nomenclatura',
            'tipo_transporte': 'Tipo de Transporte',
            'coeficiente': 'Coeficiente',
            'is_standard': '¿Estándar?',
            'proyecto': 'Proyecto',
        }
