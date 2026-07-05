from django import forms
from django.forms import ModelForm

from .models.proyecto import Proyecto


class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ["title", "mandante", "description", "date_started"]
        labels = {
            "title": "Nombre del Proyecto",
            "mandante": "Cliente / Mandante",
            "description": "Descripción del Proyecto",
            "date_started": "Fecha de Inicio",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-slate-50",
                    "placeholder": "Ej: Proyecto Autopista Norte",
                }
            ),
            "mandante": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-slate-50",
                }
            ),
            "date_started": forms.DateInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-slate-50",
                    "type": "date",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-slate-50",
                    "rows": 4,
                    "placeholder": "Descripción del proyecto...",
                }
            ),
        }
