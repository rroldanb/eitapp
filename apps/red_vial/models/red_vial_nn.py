from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models.nodo import Nodo
from apps.red_vial.models.arco import Arco


class Regulacion(BaseModel):
    """
    Tipos de regulación para movimientos en intersecciones (PARE, CEDA, SEMAFORO, LIBRE)
    """
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class Coeficiente_Cruce(BaseModel):
    coeficiente = models.FloatField(blank=False, null=False)
    tipo_transporte = models.CharField(max_length=50, blank=False, null=False)
    nomenclatura = models.CharField(max_length=10, blank=False, null=False)
    is_standard = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nomenclatura} - {self.tipo_transporte} ({self.coeficiente})"

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

# class PuntoControl(BaseModel):
#     """
#     Descripcion de punto de control (PC) en una intersección, con su regulación y flujo asociado
#     """

#     class Movimiento(models.TextChoices):
#         N1_A_N2 = '12', 'Nodo 1 → Nodo 2'
#         N1_A_N3 = '13', 'Nodo 1 → Nodo 3'
#         N1_A_N4 = '14', 'Nodo 1 → Nodo 4'
#         N1_A_N5 = '15', 'Nodo 1 → Nodo 5'
#         N1_A_N6 = '16', 'Nodo 1 → Nodo 6'
#         N2_A_N1 = '21', 'Nodo 2 → Nodo 1'
#         N2_A_N3 = '23', 'Nodo 2 → Nodo 3'
#         N2_A_N4 = '24', 'Nodo 2 → Nodo 4'
#         N2_A_N5 = '25', 'Nodo 2 → Nodo 5'
#         N2_A_N6 = '26', 'Nodo 2 → Nodo 6'
#         N3_A_N1 = '31', 'Nodo 3 → Nodo 1'
#         N3_A_N2 = '32', 'Nodo 3 → Nodo 2'
#         N3_A_N4 = '34', 'Nodo 3 → Nodo 4'
#         N3_A_N5 = '35', 'Nodo 3 → Nodo 5'
#         N3_A_N6 = '36', 'Nodo 3 → Nodo 6'
#         N4_A_N1 = '41', 'Nodo 4 → Nodo 1'
#         N4_A_N2 = '42', 'Nodo 4 → Nodo 2'
#         N4_A_N3 = '43', 'Nodo 4 → Nodo 3'
#         N4_A_N5 = '45', 'Nodo 4 → Nodo 5'
#         N4_A_N6 = '46', 'Nodo 4 → Nodo 6'
#         N5_A_N1 = '51', 'Nodo 5 → Nodo 1'
#         N5_A_N2 = '52', 'Nodo 5 → Nodo 2'
#         N5_A_N3 = '53', 'Nodo 5 → Nodo 3'
#         N5_A_N4 = '54', 'Nodo 5 → Nodo 4'
#         N5_A_N6 = '56', 'Nodo 5 → Nodo 6'
#         N6_A_N1 = '61', 'Nodo 6 → Nodo 1'
#         N6_A_N2 = '62', 'Nodo 6 → Nodo 2'
#         N6_A_N3 = '63', 'Nodo 6 → Nodo 3'
#         N6_A_N4 = '64', 'Nodo 6 → Nodo 4'
#         N6_A_N5 = '65', 'Nodo 6 → Nodo 5'

#     class Viraje(models.TextChoices):
#         DIR= 'DIR', 'Directo'
#         DER= 'DER', 'Derecha'
#         IZQ= 'IZQ', 'Izquierda'

#     nombre = models.CharField(max_length=5, blank=False, null=False)


#     nodo = models.ForeignKey(
#         Nodo,
#         on_delete=models.CASCADE,
#         related_name="pc_nodo"
#     )

#     movimiento = models.CharField(
#         max_length=2,
#         choices=Movimiento.choices,
#         blank=True,
#         null=True
#     )

#     viraje = models.CharField(
#         max_length=3,
#         choices=Viraje.choices,
#         blank=True,
#         null=True
#     )

#     is_prioritario = models.BooleanField(default=False)

#     arco_entrada = models.ForeignKey(
#         Arco,
#         on_delete=models.CASCADE,
#         related_name="pc_input"
#     )

#     #distancia = arco_entrada.longitud  # Se rescala a partir de la longitud del arco de entrada, no es un campo editable directamente

#     arco_salida = models.ForeignKey(
#         Arco,
#         on_delete=models.CASCADE,
#         related_name="pc_output"
#     )

#     # flujo_calculado = models.FloatField(blank=True, null=True) # Se llena a partir de conteos vehiculares o estimaciones, no es un campo editable directamente
#     # formula excel del flujo calculado==+IF((SUMIFS('Periodización'!$N$3:$N$1295;'Periodización'!$A$3:$A$1295;'Resumen Flujos'!A2;'Periodización'!$D$3:$D$1295;'Resumen Flujos'!C2;'Periodización'!$O$3:$O$1295;'Resumen Flujos'!$L$1))<10;10;(SUMIFS('Periodización'!$N$3:$N$1295;'Periodización'!$A$3:$A$1295;'Resumen Flujos'!A2;'Periodización'!$D$3:$D$1295;'Resumen Flujos'!C2;'Periodización'!$O$3:$O$1295;'Resumen Flujos'!$K$1)))
#     # Periodizacion es la hoja donde se ingresan los conteos vehiculares, # los encabezados de esa planilla son:
#     # PC	INTERSECCIÓN	HORA	MOV	PER	VL	TXC	TXB	C 2E	C+2E	Peat	Cicl	Moto	FTOT    Periodo
#     # FTOT es el flujo total calculado a partir de los conteos vehiculares, 
#     # # se calcula sumando los conteos de vehículos en cada categoria de vehiculo por su coeficiente de cruce correspondiente, 
#     # # ejemplo si tenemos un conteo vehicular con 100 autos (VL) y 20 camiones (TXC), y el coeficiente de cruce para autos es 1.0 y para camiones es 2.0, el flujo total calculado sería (100 * 1.0) + (20 * 2.0) = 140 vehículos/hora. 
#     # # la toma de muestras se contea cada 15 minutos
#     # Periodo puede ser PM-L periodo mañana laboral, PT-L periodo tarde laboral, PM-F periodo mañana fin de semana, PT-F periodo tarde fin de semana, PN-L periodo mediodia laboral, PN-F periodo media fin de semana, PE-L periodo noche laboral, PE-F periodo noche fin de semana 
#     # debemos definir hora de inicio y fin de cada periodo, por ejemplo:
#     # PM-L: 6:00 - 08:45
#     # PN-L: 12:00 - 14:45
#     # PT-L: 17:00 - 19:45
#     # # definir si conviene crear un modelo aparte para periodo para que sea propio para cada proyecto aunque no sean mas de 3 por proyecto ya que debe ser persistente para las tablas de periodizacion y resumen flujos.

#     # Resumen Flujos es la hoja donde se resumen los flujos calculados para cada PC, 
#     # # los encabezados de esa planilla son:
#     # PC 	LUGAR	MOV	VIR	P/S	ARCO	Distancia	Llega A	Flujo	Codigo  Periodo
#     # con esa informacion se puede calcular la siguiente tabla:
#     # COL-L COL-M COL-N
#     # ARCO (1 Vez)	Flujo Total	Vel_Modelo
#     # 06111 =+ROUND(SUMIFS($I$2:$I$69;$F$2:$F$69;L4);0) =ROUND(VLOOKUP(L4;$S$4:$W$71;5;0);0)
#     # Columnas P a W de Resumen Flujos:
#     # PC	MOV	VIR	Arco	Tipo	Intersección	Nr. Pistas	Vel_ini
#     # PC 01	13	DIR	181	Prioritarios	=+IF(T4=$T$4;1800*V4;700*V4)	2	=U4/V4/35
#     #



#     # codigo = arco_entrada.codigo_arco + "_" + arco_salida.codigo_arco # Se puede generar dinámicamente con una propiedad


#     regulacion = models.ForeignKey(
#         Regulacion,
#         on_delete=models.CASCADE,
#         related_name="pc_regulacion",
#         blank=True,
#         null=True
#     )

#     numero_pistas = models.FloatField(blank=True, null=True)

#     flujo = models.IntegerField(blank=True, null=True)  # Vehiculos/hora
#     interseccion_valor = models.FloatField(blank=True, null=True)
#     velocidad_inicial = models.FloatField(blank=True, null=True)
#     flujo_total = models.FloatField(blank=True, null=True)
#     velocidad_modelo = models.FloatField(blank=True, null=True)

#     proyecto = models.ForeignKey(
#         Proyecto,
#         on_delete=models.CASCADE,
#         related_name="puntos_control"
#     )

#     class Meta:
#         unique_together = ['nodo', 'movimiento', 'proyecto']
    
#     @property
#     def codigo_pc(self):
#         origen = f"{self.arco_entrada.codigo_arco}"
#         destino = f"{self.arco_salida.codigo_arco}"
#         return f"{origen}_{destino}"
    
#     def __str__(self):
#         return f"{self.nodo.numero} - {self.movimiento})"




