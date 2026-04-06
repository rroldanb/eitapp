from django.forms import ModelForm
from django import forms
from ..tasks.models.tasks import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'is_important', 'is_completed', 'date_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }
