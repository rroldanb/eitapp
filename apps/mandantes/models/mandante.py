from django.db import models
from apps.common.models import BaseModel

class Mandante(BaseModel):

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Contacto(BaseModel):

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    details = models.TextField(blank=True)
    mandante = models.ForeignKey(
    Mandante,
    on_delete=models.CASCADE,
    related_name="contactos"
)

    def __str__(self):
        return self.name + ' - ' + self.cargo + ' at ' + str(self.mandante.name) 

