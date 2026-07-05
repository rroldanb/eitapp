from django import forms

from apps.red_vial.models import PuntoControl

_input = (
    "w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50"
)
_select = "px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 bg-slate-50"


class PuntoControlForm(forms.ModelForm):
    class Meta:
        model = PuntoControl
        fields = [
            "nodo",
            "movimiento",
            "viraje",
            "is_prioritario",
            "arco_entrada",
            "arco_salida",
            "regulacion",
            "numero_pistas",
            "interseccion",
            "vel_ini",
            "vel_mod",
        ]
        widgets = {
            "nodo": forms.Select(
                attrs={
                    "class": _select,
                }
            ),
            "movimiento": forms.Select(
                attrs={
                    "class": _select,
                }
            ),
            "viraje": forms.Select(
                attrs={
                    "class": _select,
                }
            ),
            "is_prioritario": forms.CheckboxInput(attrs={"class": "mr-1"}),
            "arco_entrada": forms.Select(
                attrs={
                    "class": _select,
                }
            ),
            "arco_salida": forms.Select(
                attrs={
                    "class": _select,
                }
            ),
            "regulacion": forms.Select(
                attrs={
                    "class": f"w-[5rem] {_select}",
                }
            ),
            "numero_pistas": forms.NumberInput(
                attrs={
                    "class": _input.replace("w-24", "w-20"),
                    "step": "0.5",
                    "placeholder": "Pistas",
                }
            ),
            "interseccion": forms.NumberInput(
                attrs={"readonly": True, "class": f"w-[5rem] {_input}"}
            ),
            "vel_ini": forms.NumberInput(
                attrs={
                    "class": _input.replace("w-24", "w-20"),
                    "readonly": True,
                    "step": "0.1",
                    "placeholder": "0",
                }
            ),
            "vel_mod": forms.NumberInput(
                attrs={
                    "class": _input.replace("w-24", "w-20"),
                    "readonly": True,
                    "step": "1.0",
                    "placeholder": "0",
                }
            ),
        }
        labels = {
            "nodo": "Nodo",
            "movimiento": "Movimiento",
            "viraje": "Tipo de Viraje",
            "is_prioritario": "¿Es prioritario?",
            "arco_entrada": "Arco de Entrada",
            "arco_salida": "Arco de Salida",
            "regulacion": "Regulación",
            "numero_pistas": "Número de Pistas",
            "interseccion": "Intersección",
            "vel_ini": "Velocidad Inicial",
            "vel_mod": "Velocidad Modelo",
        }

    def clean(self):
        cleaned_data = super().clean()
        is_prioritario = cleaned_data.get("is_prioritario", False)
        numero_pistas = cleaned_data.get("numero_pistas")

        if numero_pistas:
            if is_prioritario:
                interseccion_val = 1800 * numero_pistas
                vel_ini_val = interseccion_val / numero_pistas / 35
            else:
                interseccion_val = 700 * numero_pistas
                vel_ini_val = 35
            cleaned_data["interseccion"] = str(int(interseccion_val))
            cleaned_data["vel_ini"] = round(vel_ini_val, 2)
            cleaned_data["vel_mod"] = round(vel_ini_val)
        else:
            cleaned_data["interseccion"] = "0"
            cleaned_data["vel_ini"] = 0
            cleaned_data["vel_mod"] = 0
        return cleaned_data

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if proyecto:
            self.fields["nodo"].queryset = (
                proyecto.nodos.filter(numero_pc__isnull=False)
                .select_related("calle_1", "calle_2")
                .order_by("numero_pc")
            )
            self.fields["nodo"].label_from_instance = lambda obj: (
                f"{obj.nombre_pc} - "
                f"{obj.calle_1.nombre if obj.calle_1 else 'Sin calle'} / "
                f"{obj.calle_2.nombre if obj.calle_2 else 'Sin intersección'}"
            )
            self.fields["arco_entrada"].queryset = proyecto.arcos.all().order_by(
                "nodo_origen__numero", "nodo_destino__numero"
            )
            self.fields["arco_salida"].queryset = proyecto.arcos.all().order_by(
                "nodo_origen__numero", "nodo_destino__numero"
            )
            self.fields["nodo"].empty_label = "Sel. Punto de Control (PC)"
            self.fields["arco_entrada"].empty_label = "Sel. arco de entrada"
            self.fields["arco_salida"].empty_label = "Sel. arco de salida"
            self.fields["regulacion"].empty_label = "Sel. regulación"
            self.fields["movimiento"].choices = [("", "Sel. movimiento")] + [
                (value, f"{value} - {label}") for value, label in self.fields["movimiento"].choices
            ]
            self.fields["viraje"].choices = [
                ("", "Sel. viraje"),
                *list(self.fields["viraje"].choices),
            ]
            self.fields["numero_pistas"].initial = 1
            self.fields["interseccion"].initial = 0
            self.fields["vel_mod"].initial = 0
            self.fields["vel_ini"].initial = 0
