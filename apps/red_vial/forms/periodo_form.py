from django import forms

from apps.red_vial.models import Periodo


class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ["codigo", "hora_inicio", "hora_fin", "es_laboral"]
        widgets = {
            "codigo": forms.Select(
                attrs={
                    "class": "form-control w-full bg-slate-50",
                    "placeholder": "Código del período",
                }
            ),
            "hora_inicio": forms.TimeInput(
                attrs={
                    "class": "form-control bg-slate-50",
                    "type": "time",
                }
            ),
            "hora_fin": forms.TimeInput(
                attrs={"class": "form-control bg-slate-50", "type": "time"}
            ),
            "es_laboral": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "codigo": "Código del Período",
            "hora_inicio": "Hora de Inicio",
            "hora_fin": "Hora de Fin",
            "es_laboral": "Es día laboral",
        }

    def __init__(self, *args, proyecto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto = proyecto
        if proyecto:
            used = Periodo.objects.filter(proyecto=proyecto).values_list("codigo", flat=True)
            if self.instance and self.instance.pk:
                used = [c for c in used if c != self.instance.codigo]
            choices = [
                (v, f"{v} - {label}" if v else label)
                for v, label in self.fields["codigo"].choices
                if not v or v not in used or (self.instance and self.instance.codigo == v)
            ]
            if not choices:
                choices = [("", "--- Todos los períodos creados ---")]
            self.fields["codigo"].choices = choices

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.proyecto:
            instance.proyecto = self.proyecto
        if commit:
            instance.save()
        return instance
