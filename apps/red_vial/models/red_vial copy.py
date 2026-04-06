from django.db import models
from apps.common.models import BaseModel
from apps.proyectos.models.proyecto import Proyecto

class Arco(BaseModel):
    nodo_origen = models.CharField(max_length=2,
        blank=False,
        null=False)
    nodo_destino = models.CharField(max_length=2,
        blank=False,
        null=False)
    longitud = models.FloatField(blank=False, null=False)
    proyecto = models.ForeignKey(
    Proyecto,
    on_delete=models.CASCADE,
    related_name="arcos"
)

    def __str__(self):
        return f"Arco {self.nodo_origen}{self.nodo_destino}'1' - {self.proyecto.title}"



class Nodo(BaseModel):

    numero = models.CharField(max_length=2, blank=False, null=False)
    plano = models.URLField(blank=True, null=True)
    imagen = models.URLField(blank=True, null=True)
    proyecto = models.ForeignKey(
    Proyecto,
    on_delete=models.CASCADE,
    related_name="nodos"
)

    def __str__(self):
        return 'Nodo ' +(str(self.numero)) + ' - ' + str(self.proyecto.title) 


class Calle(BaseModel):
    nombre = models.CharField(max_length=100, blank=False, null=False)
    numero = models.IntegerField(blank=False, null=False)
    proyecto = models.ForeignKey(
    Proyecto,
    on_delete=models.CASCADE,
        related_name="calles"
    )

    def __str__(self):
        return f"Calle {self.nombre} - {self.proyecto.title}"


    

class Coeficiente_Cruce(BaseModel):
    coeficiente = models.FloatField(blank=False, null=False)
    tipo_transporte = models.CharField(max_length=50, blank=False, null=False)
    nomenclatura = models.CharField(max_length=5, blank=False, null=False)
    is_standard = models.BooleanField(default=False)

    def __str__(self):
        return f"Coeficiente de cruce - {self.tipo_transporte}"
    
