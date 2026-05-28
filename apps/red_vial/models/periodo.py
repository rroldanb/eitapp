from apps.common.models import BaseModel
from django.db import models
from apps.proyectos.models.proyecto import Proyecto

class Periodo(BaseModel):
    """
    Período de análisis de tráfico. Cada proyecto define los suyos.
    Ejemplos: PM-L (mañana laboral), PT-L (tarde laboral), etc.
    """
    class TipoPeriodo(models.TextChoices):
        MANANA_LABORAL   = 'PM-L', 'Mañana laboral'
        MEDIODIA_LABORAL = 'PN-L', 'Mediodía laboral'
        TARDE_LABORAL    = 'PT-L', 'Tarde laboral'
        NOCHE_LABORAL    = 'PE-L', 'Noche laboral'
        MANANA_SABADO     = 'PM-S', 'Mañana sábado'
        MEDIODIA_SABADO     = 'PN-S', 'Mediodía sábado'
        TARDE_SABADO        = 'PT-S', 'Tarde sábado'
        NOCHE_SABADO        = 'PE-S', 'Noche sábado'
        MANANA_NO_LABORAL   = 'PM-F', 'Mañana no laboral'
        MEDIODIA_NO_LABORAL = 'PN-F', 'Mediodía no laboral'
        TARDE_NO_LABORAL    = 'PT-F', 'Tarde no laboral'
        NOCHE_NO_LABORAL    = 'PE-F', 'Noche no laboral'


    proyecto     = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='periodos')
    codigo       = models.CharField(max_length=4, choices=TipoPeriodo.choices)
    hora_inicio  = models.TimeField(null=True, blank=True, default=None)
    hora_fin     = models.TimeField(null=True, blank=True, default=None)
    es_laboral   = models.BooleanField(default=True)

    class Meta:
        unique_together = ['proyecto', 'codigo']

    def __str__(self):
        return f"{self.get_codigo_display()} ({self.hora_inicio:%H:%M}–{self.hora_fin:%H:%M})"

