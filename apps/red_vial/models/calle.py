from django.db import models

from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto


class Calle(BaseModel):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    numero = models.IntegerField(blank=False, null=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="calles")

    class Meta:
        unique_together = ["numero", "proyecto"]
        verbose_name = "Calle"
        verbose_name_plural = "Calles"

    def __str__(self):
        return f"{self.nombre} ({self.numero})"
