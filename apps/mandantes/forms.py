from django import forms

from apps.mandantes.models import Contacto, Mandante


class MandanteForm(forms.ModelForm):
    class Meta:
        model = Mandante
        fields = ["name", "location", "details"]
        labels = {
            "name": "Nombre",
            "location": "Ubicación",
            "details": "Detalles",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ["name", "email", "phone", "cargo", "position", "details"]
        labels = {
            "name": "Nombre",
            "email": "Correo electrónico",
            "phone": "Teléfono",
            "cargo": "Cargo",
            "position": "Posición",
            "details": "Detalles",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
