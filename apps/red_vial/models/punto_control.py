from apps.common.models import BaseModel
from django.db import models
from apps.proyectos.models.proyecto import Proyecto
from apps.red_vial.models import Nodo, Arco, Regulacion



class PuntoControl(BaseModel):
    """
    Punto de control (PC) en una intersección.
    Solo datos estructurales; los datos de flujo viven en ResumenFlujo.
    """

    class Movimiento(models.TextChoices):
        N1_A_N2 = '12', 'Nodo 1 → Nodo 2'
        N1_A_N3 = '13', 'Nodo 1 → Nodo 3'
        N1_A_N4 = '14', 'Nodo 1 → Nodo 4'
        N1_A_N5 = '15', 'Nodo 1 → Nodo 5'
        N1_A_N6 = '16', 'Nodo 1 → Nodo 6'
        N2_A_N1 = '21', 'Nodo 2 → Nodo 1'
        N2_A_N3 = '23', 'Nodo 2 → Nodo 3'
        N2_A_N4 = '24', 'Nodo 2 → Nodo 4'
        N2_A_N5 = '25', 'Nodo 2 → Nodo 5'
        N2_A_N6 = '26', 'Nodo 2 → Nodo 6'
        N3_A_N1 = '31', 'Nodo 3 → Nodo 1'
        N3_A_N2 = '32', 'Nodo 3 → Nodo 2'
        N3_A_N4 = '34', 'Nodo 3 → Nodo 4'
        N3_A_N5 = '35', 'Nodo 3 → Nodo 5'
        N3_A_N6 = '36', 'Nodo 3 → Nodo 6'
        N4_A_N1 = '41', 'Nodo 4 → Nodo 1'
        N4_A_N2 = '42', 'Nodo 4 → Nodo 2'
        N4_A_N3 = '43', 'Nodo 4 → Nodo 3'
        N4_A_N5 = '45', 'Nodo 4 → Nodo 5'
        N4_A_N6 = '46', 'Nodo 4 → Nodo 6'
        N5_A_N1 = '51', 'Nodo 5 → Nodo 1'
        N5_A_N2 = '52', 'Nodo 5 → Nodo 2'
        N5_A_N3 = '53', 'Nodo 5 → Nodo 3'
        N5_A_N4 = '54', 'Nodo 5 → Nodo 4'
        N5_A_N6 = '56', 'Nodo 5 → Nodo 6'
        N6_A_N1 = '61', 'Nodo 6 → Nodo 1'
        N6_A_N2 = '62', 'Nodo 6 → Nodo 2'
        N6_A_N3 = '63', 'Nodo 6 → Nodo 3'
        N6_A_N4 = '64', 'Nodo 6 → Nodo 4'
        N6_A_N5 = '65', 'Nodo 6 → Nodo 5'

    class Viraje(models.TextChoices):
        DIR = 'DIR', 'Directo'
        DER = 'DER', 'Derecha'
        IZQ = 'IZQ', 'Izquierda'

    # nombre         = models.CharField(max_length=5)
    proyecto       = models.ForeignKey(Proyecto,on_delete=models.CASCADE,related_name="puntos_control")
    nodo           = models.ForeignKey(Nodo, on_delete=models.CASCADE, related_name='pc_nodo')
    movimiento     = models.CharField(max_length=2, choices=Movimiento.choices, blank=False, null=False)
    viraje         = models.CharField(max_length=3, choices=Viraje.choices, blank=True, null=True)
    is_prioritario = models.BooleanField(default=False)
    arco_entrada   = models.ForeignKey(Arco, on_delete=models.CASCADE, related_name='pc_input')
    arco_salida    = models.ForeignKey(Arco, on_delete=models.CASCADE, related_name='pc_output')
    regulacion     = models.ForeignKey(Regulacion, on_delete=models.SET_NULL, related_name='pc_regulacion', blank=True, null=True)
    numero_pistas  = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ['nodo', 'movimiento', 'proyecto']
        verbose_name = "Punto_Control"
        verbose_name_plural = "Puntos_Control"
        
    # @property
    # def codigo_pc(self):
    #     return f"{self.arco_entrada.codigo_arco}_{self.arco_salida.codigo_arco}"
    @property
    def nombre(self):
        """PC-03 o 'Sin PC' si el nodo no tiene numero_pc."""
        return self.nodo.nombre_pc or f"Nodo-{self.nodo.numero}"

    @property
    def codigo_pc(self):
        return f"{self.arco_entrada.codigo_arco}_{self.arco_salida.codigo_arco}"
    
    @property
    def distancia(self):
        return self.arco_entrada.longitud

    def __str__(self):
        # return f"{self.nombre} ({self.nodo.numero} - {self.movimiento})"
        return f"{self.nombre} | Mov {self.movimiento} | {self.viraje or '—'}"
    