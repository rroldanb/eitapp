from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from .red_vial import Nodo, NodoMovimiento


class Periodo(BaseModel):
    """
    Períodos de medición de tráfico (ej: PM-L = Pico Mañana Laboral)
    """
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    tipo_dia = models.CharField(
        max_length=20,
        choices=[
            ('laboral', 'Día Laboral'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo/Festivo'),
        ],
        default='laboral'
    )

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ConteoVehicular(BaseModel):
    """
    Conteos vehiculares por período, nodo y movimiento
    """
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="conteos_vehiculares"
    )
    nodo = models.ForeignKey(
        Nodo,
        on_delete=models.CASCADE,
        related_name="conteos"
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name="conteos"
    )
    hora = models.TimeField()

    # Campos para cada tipo de vehículo (según Excel)
    vl = models.FloatField(null=True, blank=True, verbose_name="VL")  # Vehículos Livianos
    txc = models.FloatField(null=True, blank=True, verbose_name="TXC")  # Taxi Colectivo
    txb = models.FloatField(null=True, blank=True, verbose_name="TXB")  # Taxi Básico
    c_2e = models.FloatField(null=True, blank=True, verbose_name="C 2E")  # Camión 2 Ejes
    c_mas_2e = models.FloatField(null=True, blank=True, verbose_name="C+2E")  # Camión +2 Ejes
    peaton = models.FloatField(null=True, blank=True, verbose_name="Peat")  # Peatón
    ciclista = models.FloatField(null=True, blank=True, verbose_name="Cicl")  # Ciclista
    moto = models.FloatField(null=True, blank=True, verbose_name="Moto")  # Motocicleta

    # Total en vehículos equivalentes
    vehiculos_equivalentes = models.FloatField(null=True, blank=True, verbose_name="VEQ")

    class Meta:
        unique_together = ['proyecto', 'nodo', 'periodo', 'hora']
        ordering = ['hora']

    def __str__(self):
        return f"{self.nodo.numero} - {self.hora} ({self.periodo.codigo})"


class FlujoMovimiento(BaseModel):
    """
    Flujos de tráfico específicos por movimiento
    """
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="flujos_movimiento"
    )
    nodo_movimiento = models.ForeignKey(
        NodoMovimiento,
        on_delete=models.CASCADE,
        related_name="flujos"
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name="flujos_movimiento"
    )
    hora = models.TimeField()
    flujo_veh_hora = models.FloatField(null=True, blank=True, verbose_name="Flujo (veh/h)")
    flujo_veq_15min = models.FloatField(null=True, blank=True, verbose_name="VEQ/15min")
    flujo_veq_hora = models.FloatField(null=True, blank=True, verbose_name="VEQ/h")

    class Meta:
        unique_together = ['proyecto', 'nodo_movimiento', 'periodo', 'hora']
        ordering = ['hora']

    def __str__(self):
        return f"{self.nodo_movimiento} - {self.hora}"
