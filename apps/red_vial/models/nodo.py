from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models.calle import Calle

class Nodo(BaseModel):
    numero = models.IntegerField( blank=False, null=False)
    interseccion = models.CharField(max_length=200, blank=True, null=True)
    plano = models.URLField(blank=True, null=True)
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
    # is_pc = models.BooleanField(default=False)  # Indica si es un Punto de control (PC)
    numero_pc    = models.PositiveSmallIntegerField(blank=True, null=True, unique=False,
                   help_text="Número del PC asociado (ej: 3 → PC-03). Null si no es PC.")

    class Meta:
        unique_together = ['numero', 'proyecto']

    @property
    def is_pc(self):
        """Un nodo es PC si tiene numero_pc asignado."""
        return self.numero_pc is not None

    @property
    def nombre_pc(self):
        """Retorna 'PC-03' o None."""
        return f"PC-{self.numero_pc:02d}" if self.is_pc else None

    def __str__(self):
        pc_tag = f" [{self.nombre_pc}]" if self.is_pc else ""
        calle_1_nombre = self.calle_1.nombre if self.calle_1 else 'Sin calle'
        calle_2_nombre = self.calle_2.nombre if self.calle_2 else 'Sin intersección'
        # return f"{self.numero}{pc_tag} - {calle_1_nombre} / {calle_2_nombre}"

        return f"{self.numero} - {calle_1_nombre} / {calle_2_nombre}"
