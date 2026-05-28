from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models.calle import Calle

class Nodo(BaseModel):
    is_pc = models.BooleanField(default=False)  # Indica si es un Punto de control (PC)
    numero_pc = models.IntegerField(blank=True, null=True) # Solo para PCs
    interseccion = models.CharField(max_length=200, blank=True, null=True)
    plano = models.URLField(blank=True, null=True)
    numero = models.IntegerField( blank=False, null=False)
    imagen = models.URLField(blank=True, null=True)
    calle_1 = models.ForeignKey(
        Calle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nodos_calle_1"
    )
    calle_2 = models.ForeignKey(
        Calle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nodos_calle_2"
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="nodos"
    )

    class Meta:
        unique_together = ['numero', 'proyecto']

    def __str__(self):
        calle_1_nombre = self.calle_1.nombre if self.calle_1 else 'Sin calle'
        calle_2_nombre = self.calle_2.nombre if self.calle_2 else 'Sin intersección'

        return f"{self.numero} - {calle_1_nombre} / {calle_2_nombre}"
