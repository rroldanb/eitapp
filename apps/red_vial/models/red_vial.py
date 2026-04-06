from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto


class Calle(BaseModel):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    numero = models.IntegerField(blank=False, null=False)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="calles"
    )

    class Meta:
        unique_together = ['numero', 'proyecto']
        verbose_name = "Calle"
        verbose_name_plural = "Calles"

    def __str__(self):
        return f"{self.nombre} ({self.numero})"


class Nodo(BaseModel):
    numero = models.CharField(max_length=10, blank=False, null=False)
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

    class Meta:
        unique_together = ['numero', 'proyecto']

    def __str__(self):
        return f"Nodo {self.numero} - {self.interseccion or 'Sin intersección'}"


class Arco(BaseModel):
    nodo_origen = models.ForeignKey(
        Nodo,
        on_delete=models.CASCADE,
        related_name="arcos_salida"
    )
    nodo_destino = models.ForeignKey(
        Nodo,
        on_delete=models.CASCADE,
        related_name="arcos_entrada"
    )
    longitud = models.FloatField(blank=False, null=False)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="arcos"
    )

    class Meta:
        unique_together = ['nodo_origen', 'nodo_destino', 'proyecto']

    def __str__(self):
        return f"Arco {self.nodo_origen.numero} → {self.nodo_destino.numero}"


class Movimiento(BaseModel):
    """
    Tipos de movimiento en una intersección (DIR=Directo, DER=Derecha, IZQ=Izquierda)
    """
    codigo = models.CharField(max_length=2, unique=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class NodoMovimiento(BaseModel):
    """
    Configuración de movimientos permitidos en un nodo/intersección
    """
    class TipoPrioridad(models.TextChoices):
        PRIORITARIO = 'P', 'Prioritario'
        SECUNDARIO = 'S', 'Secundario'

    class TipoRegulacion(models.TextChoices):
        PARE = 'Pare', 'Pare'
        CEDA = 'Ceda', 'Ceda el paso'
        SEMAFORO = 'Semaforo', 'Semáforo'
        LIBRE = 'Libre', 'Libre'

    nodo = models.ForeignKey(
        Nodo,
        on_delete=models.CASCADE,
        related_name="movimientos_config"
    )
    movimiento = models.ForeignKey(
        Movimiento,
        on_delete=models.CASCADE,
        related_name="configuraciones"
    )
    arco_entrada = models.ForeignKey(
        Arco,
        on_delete=models.CASCADE,
        related_name="movimientos_entrada"
    )
    arco_salida = models.ForeignKey(
        Arco,
        on_delete=models.CASCADE,
        related_name="movimientos_salida"
    )
    tipo_prioridad = models.CharField(
        max_length=1,
        choices=TipoPrioridad.choices
    )
    regulacion = models.CharField(
        max_length=20,
        choices=TipoRegulacion.choices,
        blank=True,
        null=True
    )
    interseccion_valor = models.FloatField(blank=True, null=True)
    numero_pistas = models.FloatField(blank=True, null=True)
    velocidad_inicial = models.FloatField(blank=True, null=True)
    flujo_total = models.FloatField(blank=True, null=True)
    velocidad_modelo = models.FloatField(blank=True, null=True)
    flujo = models.IntegerField(blank=True, null=True)  # Vehiculos/hora
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="nodos_movimientos"
    )

    class Meta:
        unique_together = ['nodo', 'movimiento', 'proyecto']

    def __str__(self):
        return f"{self.nodo.numero} - Mov {self.movimiento.codigo} ({self.get_tipo_prioridad_display()})"


class Coeficiente_Cruce(BaseModel):
    coeficiente = models.FloatField(blank=False, null=False)
    tipo_transporte = models.CharField(max_length=50, blank=False, null=False)
    nomenclatura = models.CharField(max_length=10, blank=False, null=False)
    is_standard = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nomenclatura} - {self.tipo_transporte} ({self.coeficiente})"
