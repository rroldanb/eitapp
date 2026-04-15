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

    @property
    def codigo_arco(self):
        origen = f"{self.nodo_origen.numero:02}"
        destino = f"{self.nodo_destino.numero:02}"
        return f"{origen}{destino}1"

    def __str__(self):
        return f"Arco {self.codigo_arco} (Longitud: {self.longitud} m)"

class Regulacion(BaseModel):
    """
    Tipos de regulación para movimientos en intersecciones (PARE, CEDA, SEMAFORO, LIBRE)
    """
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class NodoMovimiento(BaseModel):
    """
    Configuración de movimientos permitidos en un nodo/intersección
    """
    class TipoPrioridad(models.TextChoices):
        PRIORITARIO = 'P', 'Prioritario'
        SECUNDARIO = 'S', 'Secundario'

    class Movimiento(models.TextChoices):
        DIR='Directo'
        DER='Derecha'
        IZQ='Izquierda'

    nodo = models.ForeignKey(
        Nodo,
        on_delete=models.CASCADE,
        related_name="movimientos_config"
    )
    movimiento = models.CharField(
        max_length=10,
        choices=Movimiento.choices,
        blank=True,
        null=True
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
    regulacion = models.ForeignKey(
        Regulacion,
        on_delete=models.CASCADE,
        related_name="regulaciones_movimiento",
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
        return f"{self.nodo.numero} - {self.movimiento})"

class PuntoControl(BaseModel):
    """
    Descripcion de punto de control (PC) en una intersección, con su regulación y flujo asociado
    """

    class Movimiento(models.TextChoices):
        N1_A_N2 = '12', 'Nodo 1 → Nodo 2'
        N1_A_N3 = '13', 'Nodo 1 → Nodo 3'
        N1_A_N4 = '14', 'Nodo 1 → Nodo 4'
        N2_A_N1 = '21', 'Nodo 2 → Nodo 1'
        N2_A_N3 = '23', 'Nodo 2 → Nodo 3'
        N2_A_N4 = '24', 'Nodo 2 → Nodo 4'
        N3_A_N1 = '31', 'Nodo 3 → Nodo 1'
        N3_A_N2 = '32', 'Nodo 3 → Nodo 2'
        N3_A_N4 = '34', 'Nodo 3 → Nodo 4'
        N4_A_N1 = '41', 'Nodo 4 → Nodo 1'
        N4_A_N2 = '42', 'Nodo 4 → Nodo 2'
        N4_A_N3 = '43', 'Nodo 4 → Nodo 3'
        #hasta el 64 para intersecciones con hasta 6 nodos

    class Viraje(models.TextChoices):
        DIR= 'DIR', 'Directo'
        DER= 'DER', 'Derecha'
        IZQ= 'IZQ', 'Izquierda'


    nodo = models.ForeignKey(
        Nodo,
        on_delete=models.CASCADE,
        related_name="pc_nodo"
    )

    movimiento = models.CharField(
        max_length=2,
        choices=Movimiento.choices,
        blank=True,
        null=True
    )

    viraje = models.CharField(
        max_length=3,
        choices=Viraje.choices,
        blank=True,
        null=True
    )

    is_prioritario = models.BooleanField(default=False)

    arco_entrada = models.ForeignKey(
        Arco,
        on_delete=models.CASCADE,
        related_name="pc_input"
    )
    arco_salida = models.ForeignKey(
        Arco,
        on_delete=models.CASCADE,
        related_name="pc_output"
    )

    regulacion = models.ForeignKey(
        Regulacion,
        on_delete=models.CASCADE,
        related_name="pc_regulacion",
        blank=True,
        null=True
    )

    numero_pistas = models.FloatField(blank=True, null=True)

    flujo = models.IntegerField(blank=True, null=True)  # Vehiculos/hora
    interseccion_valor = models.FloatField(blank=True, null=True)
    velocidad_inicial = models.FloatField(blank=True, null=True)
    flujo_total = models.FloatField(blank=True, null=True)
    velocidad_modelo = models.FloatField(blank=True, null=True)

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="puntos_control"
    )

    class Meta:
        unique_together = ['nodo', 'movimiento', 'proyecto']
    
    @property
    def codigo_pc(self):
        origen = f"{self.arco_entrada.codigo_arco}"
        destino = f"{self.arco_salida.codigo_arco}"
        return f"{origen}_{destino}"
    
    def __str__(self):
        return f"{self.nodo.numero} - {self.movimiento})"


class Coeficiente_Cruce(BaseModel):
    coeficiente = models.FloatField(blank=False, null=False)
    tipo_transporte = models.CharField(max_length=50, blank=False, null=False)
    nomenclatura = models.CharField(max_length=10, blank=False, null=False)
    is_standard = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nomenclatura} - {self.tipo_transporte} ({self.coeficiente})"
