from django.contrib.auth.models import User
from django.db import models

from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto


class TaskStatus(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    EN_PROGRESO = "en_progreso", "En Progreso"
    COMPLETADA = "completada", "Completada"
    CANCELADA = "cancelada", "Cancelada"


class Task(BaseModel):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDIENTE
    )
    is_important = models.BooleanField(default=False)
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks")
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    due_date = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
