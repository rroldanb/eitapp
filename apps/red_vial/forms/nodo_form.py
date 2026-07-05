from django import forms
from django.core.exceptions import ValidationError

from apps.red_vial.models import Nodo


class NodoForm(forms.ModelForm):
    class Meta:
        model = Nodo
        fields = ["numero", "interseccion", "calle_1", "calle_2", "plano", "imagen", "numero_pc"]
        widgets = {
            "numero": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: PC 01"}),
            "interseccion": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej: Av. Huasco con Armando Rossel"}
            ),
            "calle_1": forms.Select(attrs={"class": "form-control"}),
            "calle_2": forms.Select(attrs={"class": "form-control"}),
            "numero_pc": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Número de PC (si aplica)"}
            ),
            "plano": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "URL del plano"}
            ),
            "imagen": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "URL de la imagen"}
            ),
        }
        labels = {
            "numero": "Número del Nodo",
            "interseccion": "Descripción de la Intersección",
            "calle_1": "Calle 1",
            "calle_2": "Calle 2",
            "numero_pc": "Número de PC (si es aplicable)",
            "plano": "URL del Plano",
            "imagen": "URL de la Imagen",
        }

    def __init__(self, *args, **kwargs):
        self.proyecto = kwargs.pop("proyecto", None)
        super().__init__(*args, **kwargs)
        proyecto = self.proyecto or getattr(self.instance, "proyecto", None)
        if proyecto:
            self.fields["calle_1"].queryset = proyecto.calles.all()
            self.fields["calle_2"].queryset = proyecto.calles.all()

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get("numero")
        proyecto = self.proyecto or getattr(self.instance, "proyecto", None)
        if numero and proyecto:
            qs = Nodo.objects.filter(numero=numero, proyecto=proyecto)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                msg = f"Ya existe un nodo con el número {numero} en este proyecto."
                raise ValidationError({"numero": msg})
        return cleaned_data
