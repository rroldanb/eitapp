from django.db import models

from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models.nodo import Nodo


class Arco(BaseModel):
    nodo_origen = models.ForeignKey(Nodo, on_delete=models.CASCADE, related_name="arcos_salida")
    nodo_destino = models.ForeignKey(Nodo, on_delete=models.CASCADE, related_name="arcos_entrada")
    longitud = models.FloatField(blank=False, null=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="arcos")

    class Meta:
        unique_together = ["nodo_origen", "nodo_destino", "proyecto"]

    @property
    def codigo_arco(self):
        origen = f"{self.nodo_origen.numero:02}"
        destino = f"{self.nodo_destino.numero:02}"
        return f"{origen}{destino}1"

    def __str__(self):
        return f"{self.codigo_arco} (nodos {self.nodo_origen.numero} → {self.nodo_destino.numero})"
