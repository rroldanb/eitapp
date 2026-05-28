from apps.common.models import BaseModel
from django.db import models
from apps.red_vial.models import PuntoControl, Periodo


# Coeficientes de equivalencia por tipo de vehículo
COEF_CRUCE = {
    'vl':      1.0,   # Vehículo liviano
    'txc':     2.0,   # Taxi colectivo
    'txb':     2.0,   # Taxi básico
    'c2e':     2.5,   # Camión 2 ejes
    'c_mas2e': 3.5,   # Camión +2 ejes
    'peat':    0.2,   # Peatón
    'cicl':    0.5,   # Ciclista
    'moto':    0.75,  # Motocicleta
}

class Periodizacion(BaseModel):
    """
    Conteo vehicular crudo por intervalo de 15 minutos.
    FTOT se calcula dinámicamente como property.
    """
    pc      = models.ForeignKey(PuntoControl, on_delete=models.CASCADE, related_name='periodizaciones')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='periodizaciones')
    hora    = models.TimeField(help_text="Hora de inicio del intervalo de 15 min")

    vl      = models.PositiveIntegerField(default=0, verbose_name="Vehículo liviano")
    txc     = models.PositiveIntegerField(default=0, verbose_name="Taxi colectivo")
    txb     = models.PositiveIntegerField(default=0, verbose_name="Taxi básico")
    c2e     = models.PositiveIntegerField(default=0, verbose_name="Camión 2 ejes")
    c_mas2e = models.PositiveIntegerField(default=0, verbose_name="Camión +2 ejes")
    peat    = models.PositiveIntegerField(default=0, verbose_name="Peatón")
    cicl    = models.PositiveIntegerField(default=0, verbose_name="Ciclista")
    moto    = models.PositiveIntegerField(default=0, verbose_name="Motocicleta")

    class Meta:
        unique_together = ['pc', 'periodo', 'hora']
        ordering = ['periodo', 'hora']

    @property
    def ftot(self) -> float:
        """Flujo total ponderado por coeficientes de equivalencia."""
        total = sum(
            getattr(self, campo) * coef
            for campo, coef in COEF_CRUCE.items()
        )
        return round(total, 2)

    def __str__(self):
        return f"{self.pc.nombre} | {self.periodo.codigo} | {self.hora:%H:%M}"

