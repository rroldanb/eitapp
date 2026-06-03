from django.db import models
from django.db.models import Sum, Avg, Count
from apps.common.models import BaseModel
from apps.red_vial.models import Periodizacion, PuntoControl, Periodo


class ResumenFlujo(BaseModel):
    pc      = models.ForeignKey(PuntoControl, on_delete=models.CASCADE, related_name='resumenes')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='resumenes')

    flujo              = models.IntegerField(blank=True, null=True, help_text="Flujo calculado (mín. 10 veh/h)")
    flujo_total        = models.FloatField(blank=True, null=True)
    promedio           = models.FloatField(blank=True, null=True, help_text="Promedio de ftot por registro de 15 min")
    num_registros      = models.IntegerField(blank=True, null=True, help_text="Número de registros de Periodización agregados")
    interseccion_valor = models.FloatField(blank=True, null=True)
    velocidad_inicial  = models.FloatField(blank=True, null=True)
    velocidad_modelo   = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ['pc', 'periodo']

    def calcular_flujo(self) -> int:
        total = Periodizacion.objects.filter(
            pc=self.pc,
            periodo=self.periodo,
        ).aggregate(suma=Sum('ftot'))['suma'] or 0
        return max(10, round(total))

    def save(self, *args, **kwargs):
        if self.flujo is None:
            self.flujo = self.calcular_flujo()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pc.nombre} | {self.periodo.codigo} | flujo={self.flujo}"
    