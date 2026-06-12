from django.db import models
from apps.common.models import BaseModel


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

