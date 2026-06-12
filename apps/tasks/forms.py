from django import forms
from .models.tasks import Task, TaskStatus


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'is_important', 'assignee', 'proyecto', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from apps.usuarios.models import Role
            role = user.profile.role if hasattr(user, 'profile') else Role.ENCUESTADOR
            if role == Role.ENCUESTADOR:
                self.fields['assignee'].queryset = user.__class__.objects.filter(id=user.id)
                self.fields['assignee'].initial = user
            elif role == Role.MODELADOR:
                self.fields['assignee'].queryset = user.__class__.objects.filter(profile__role=Role.ENCUESTADOR)
            elif role == Role.ADMIN:
                self.fields['assignee'].queryset = user.__class__.objects.all()


class BulkTaskForm(forms.Form):
    titles = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Una tarea por línea'}))
    assignee = forms.ModelChoiceField(queryset=None, required=False)
    proyecto = forms.ModelChoiceField(queryset=None, required=False)
    due_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from apps.usuarios.models import Role
            from apps.proyectos.models.proyecto import Proyecto
            role = user.profile.role if hasattr(user, 'profile') else Role.ENCUESTADOR
            if role == Role.ADMIN:
                self.fields['assignee'].queryset = user.__class__.objects.all()
            else:
                self.fields['assignee'].queryset = user.__class__.objects.filter(profile__role=Role.ENCUESTADOR)
            self.fields['proyecto'].queryset = Proyecto.objects.all()
