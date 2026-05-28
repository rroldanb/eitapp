from django.db import models
from apps.common.models import BaseModel
from apps.red_vial.models.coeficiente_cruce import CoeficienteCruce


class Periodizacion(BaseModel):
    pc      = models.ForeignKey('PuntoControl', on_delete=models.CASCADE, related_name='conteos')
    periodo = models.ForeignKey('Periodo', on_delete=models.CASCADE, related_name='conteos')
    hora    = models.TimeField()

    # Campos de conteo — nombres alineados con nomenclatura de CoeficienteCruce
    vl      = models.PositiveIntegerField(default=0)
    txc     = models.PositiveIntegerField(default=0)
    txb     = models.PositiveIntegerField(default=0)
    c2e     = models.PositiveIntegerField(default=0)
    c_mas2e = models.PositiveIntegerField(default=0)
    peat    = models.PositiveIntegerField(default=0)
    cicl    = models.PositiveIntegerField(default=0)
    moto    = models.PositiveIntegerField(default=0)

    ftot = models.FloatField(default=0, editable=False)

    class Meta:
        unique_together = ['pc', 'periodo', 'hora']

    def calcular_ftot(self) -> float:
        """
        Resuelve coeficientes desde el proyecto del PC,
        respetando la herencia estándar → proyecto.
        """
        coefs = CoeficienteCruce.objects.resolver_para_proyecto(
            self.pc.proyecto
        )
        total = sum(
            getattr(self, nomenclatura, 0) * coef
            for nomenclatura, coef in coefs.items()
        )
        return round(total, 2)

    def save(self, *args, **kwargs):
        self.ftot = self.calcular_ftot()
        super().save(*args, **kwargs)
