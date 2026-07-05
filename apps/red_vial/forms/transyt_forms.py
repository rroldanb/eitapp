from django import forms

from apps.red_vial.models.transyt import ConfiguracionTransyt, FaseSemaforica, ParametroArco


class ConfiguracionTransytForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionTransyt
        fields = ["ciclo", "W", "K", "perdida_inicial", "ganancia_final"]
        widgets = {
            "ciclo": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "min": "1",
                }
            ),
            "W": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.01",
                }
            ),
            "K": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.01",
                }
            ),
            "perdida_inicial": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.1",
                }
            ),
            "ganancia_final": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.1",
                }
            ),
        }
        labels = {
            "ciclo": "Ciclo (seg)",
            "W": "Costo demora W ($/hr-veh)",
            "K": "Costo detención K ($/det)",
            "perdida_inicial": "Pérdida inicial (seg)",
            "ganancia_final": "Ganancia final (seg)",
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proyecto:
            instance.proyecto = self.proyecto
        if commit:
            instance.save()
        return instance


class ParametroArcoForm(forms.ModelForm):
    class Meta:
        model = ParametroArco
        fields = [
            "punto_control",
            "flujo_saturacion",
            "ponderador_demora",
            "ponderador_detencion",
            "capacidad_cola",
            "tiene_tarjeta_38",
        ]
        widgets = {
            "punto_control": forms.Select(
                attrs={
                    "class": " w-68 px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                }
            ),
            "flujo_saturacion": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "10",
                }
            ),
            "ponderador_demora": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.01",
                }
            ),
            "ponderador_detencion": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.01",
                }
            ),
            "capacidad_cola": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.1",
                }
            ),
            "tiene_tarjeta_38": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        labels = {
            "punto_control": "Punto de Control",
            "flujo_saturacion": "Flujo Sat. (ADE/hr)",
            "ponderador_demora": "Pond. Demora (wᵢ)",
            "ponderador_detencion": "Pond. Detención (kᵢ)",
            "capacidad_cola": "Cap. Cola (ADE)",
            "tiene_tarjeta_38": "Tarjeta 38",
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        if proyecto:
            self.fields["punto_control"].queryset = proyecto.puntos_control.select_related(
                "nodo"
            ).order_by("nodo__numero_pc", "nodo__numero")
            self.fields["punto_control"].label_from_instance = lambda obj: (
                f"{obj.nombre} — Mov {obj.get_movimiento_display() or obj.movimiento}"
            )
            self.fields["punto_control"].empty_label = "Sel. Punto de Control"

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proyecto:
            instance.proyecto = self.proyecto
        if commit:
            instance.save()
        return instance


class FaseSemaforicaForm(forms.ModelForm):
    class Meta:
        model = FaseSemaforica
        fields = ["punto_control", "fase_numero", "verde_inicio", "verde_fin"]
        widgets = {
            "punto_control": forms.Select(
                attrs={
                    "class": "w-full max-w-[180px] px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                }
            ),
            "fase_numero": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "min": "1",
                }
            ),
            "verde_inicio": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.1",
                }
            ),
            "verde_fin": forms.NumberInput(
                attrs={
                    "class": "w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500 bg-slate-50",
                    "step": "0.1",
                }
            ),
        }
        labels = {
            "punto_control": "Punto de Control",
            "fase_numero": "N° Fase",
            "verde_inicio": "Verde Inicio (seg)",
            "verde_fin": "Verde Fin (seg)",
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        if proyecto:
            self.fields["punto_control"].queryset = proyecto.puntos_control.select_related(
                "nodo"
            ).order_by("nodo__numero_pc", "nodo__numero")
            self.fields["punto_control"].label_from_instance = lambda obj: (
                f"{obj.nombre} — Mov {obj.get_movimiento_display() or obj.movimiento}"
            )
            self.fields["punto_control"].empty_label = "Sel. Punto de Control"

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proyecto:
            instance.proyecto = self.proyecto
        if commit:
            instance.save()
        return instance
