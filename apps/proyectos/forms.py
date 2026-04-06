from django.forms import ModelForm
from django import forms
from .models.proyecto import Proyecto

class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ['title', 'mandante', 'description', 'date_started']
        labels = {
            'title': 'Nombre del Proyecto',
            'mandante': 'Cliente / Mandante',
            'description': 'Descripción del Proyecto',
            'date_started': 'Fecha de Inicio',
        }
        widgets = {
            'title': forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ej: Proyecto Autopista Norte'
    }),
            'mandante': forms.Select(attrs={'class': 'form-control'}),
            'date_started': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
