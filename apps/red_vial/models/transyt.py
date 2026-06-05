from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models.punto_control import PuntoControl


class ConfiguracionTransyt(BaseModel):
    proyecto = models.OneToOneField(
        Proyecto, on_delete=models.CASCADE, related_name='configuracion_transyt'
    )
    ciclo = models.PositiveIntegerField(
        default=60, help_text='Tiempo de ciclo en segundos'
    )
    W = models.FloatField(
        default=10.0, help_text='Costo por hora de demora ($/hr-veh) — Tarjeta 1'
    )
    K = models.FloatField(
        default=0.5, help_text='Costo por detención ($/det) — Tarjeta 1'
    )
    perdida_inicial = models.FloatField(
        default=2.0, help_text='Pérdida inicial en segundos — Tarjeta 1'
    )
    ganancia_final = models.FloatField(
        default=1.0, help_text='Ganancia final en segundos — Tarjeta 1'
    )

    class Meta:
        verbose_name = 'Configuración TRANSYT'
        verbose_name_plural = 'Configuraciones TRANSYT'

    def __str__(self):
        return f'TRANSYT — {self.proyecto.title} (ciclo={self.ciclo}s)'


class ParametroArco(BaseModel):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='parametros_arco'
    )
    punto_control = models.OneToOneField(
        PuntoControl, on_delete=models.CASCADE, related_name='parametro_arco'
    )
    flujo_saturacion = models.FloatField(
        default=1800.0, help_text='Flujo de saturación en ADE/hr verde — Tarjeta 30/31'
    )
    ponderador_demora = models.FloatField(
        default=1.0, help_text='Ponderador w_i para costo de demora — Tarjeta 30/31'
    )
    ponderador_detencion = models.FloatField(
        default=1.0, help_text='Ponderador k_i para costo de detención — Tarjeta 30/31'
    )
    capacidad_cola = models.FloatField(
        blank=True, null=True, help_text='Capacidad física de cola en ADE — Tarjeta 38'
    )
    tiene_tarjeta_38 = models.BooleanField(
        default=False, help_text='Si tiene Tarjeta 38, el exceso de cola se suma al IR'
    )

    class Meta:
        verbose_name = 'Parámetro de Arco'
        verbose_name_plural = 'Parámetros de Arco (Tarjetas 30/31/38)'

    def __str__(self):
        return f'Param {self.punto_control.codigo_pc} — S={self.flujo_saturacion}'


class FaseSemaforica(BaseModel):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name='fases_semaforicas'
    )
    punto_control = models.ForeignKey(
        PuntoControl, on_delete=models.CASCADE, related_name='fases_semaforicas'
    )
    fase_numero = models.PositiveSmallIntegerField(
        help_text='Número de fase semafórica'
    )
    verde_inicio = models.FloatField(
        help_text='Inicio del verde en segundos'
    )
    verde_fin = models.FloatField(
        help_text='Fin del verde en segundos'
    )

    class Meta:
        verbose_name = 'Fase Semafórica'
        verbose_name_plural = 'Fases Semafóricas'
        unique_together = ['punto_control', 'fase_numero']

    def __str__(self):
        return f'Fase {self.fase_numero} — PC {self.punto_control.codigo_pc} ({self.verde_inicio}s–{self.verde_fin}s)'
