from django import forms
from .models.tasks import Task, TaskStatus


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'is_important', 'assignee', 'proyecto', 'due_date']
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'status': 'Estado',
            'is_important': 'Importante',
            'assignee': 'Asignado a',
            'proyecto': 'Proyecto',
            'due_date': 'Fecha de vencimiento',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent', 'rows': 3, 'oninput': 'this.style.height="";this.style.height=Math.min(this.scrollHeight, 300)+"px"'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500'}),
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
    titles = forms.CharField(
        label='Títulos',
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Una tarea por línea'})
    )
    assignee = forms.ModelChoiceField(label='Asignado a', queryset=None, required=False)
    proyecto = forms.ModelChoiceField(label='Proyecto', queryset=None, required=False)
    due_date = forms.DateTimeField(
        label='Fecha de vencimiento', required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )

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
