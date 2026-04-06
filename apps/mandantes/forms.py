from django import forms
from apps.mandantes.models import Mandante, Contacto


class MandanteForm(forms.ModelForm):

    class Meta:
        model = Mandante
        fields = ["name", "location", "details"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ContactoForm(forms.ModelForm):

    class Meta:
        model = Contacto
        fields = ["name", "email", "phone","cargo", "position", "details"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "details": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }



