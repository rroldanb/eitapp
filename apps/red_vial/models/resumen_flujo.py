from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models import Periodizacion, PuntoControl, Periodo



class ResumenFlujo(BaseModel):
    """
    Resumen de flujos calculados por PC y período.
    Equivale a la hoja 'Resumen Flujos' de la planilla Excel.
    El flujo se calcula con un mínimo de 10 veh/h (equivalente al IF en la fórmula Excel).
    """
    pc      = models.ForeignKey(PuntoControl, on_delete=models.CASCADE, related_name='resumenes')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='resumenes')

    flujo              = models.IntegerField(blank=True, null=True, help_text="Flujo calculado (mín. 10 veh/h)")
    flujo_total        = models.FloatField(blank=True, null=True)
    interseccion_valor = models.FloatField(blank=True, null=True)
    velocidad_inicial  = models.FloatField(blank=True, null=True)
    velocidad_modelo   = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ['pc', 'periodo']

    def calcular_flujo(self) -> int:
        """
        Replica la lógica Excel:
        =IF(SUMIFS(...) < 10, 10, SUMIFS(...))
        """
        from django.db.models import Sum
        total = Periodizacion.objects.filter(
            pc=self.pc,
            periodo=self.periodo,
        ).aggregate(suma=Sum('ftot'))['suma'] or 0  # ftot aún no es campo DB

        # Nota: si ftot se persiste como campo, usar aggregate directamente.
        # Si sigue siendo property, iterar conteos y sumar manualmente:
        conteos = Periodizacion.objects.filter(pc=self.pc, periodo=self.periodo)
        suma_ftot = sum(c.ftot for c in conteos)
        return max(10, round(suma_ftot))

    def save(self, *args, **kwargs):
        if self.flujo is None:
            self.flujo = self.calcular_flujo()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pc.nombre} | {self.periodo.codigo} | flujo={self.flujo}"
    