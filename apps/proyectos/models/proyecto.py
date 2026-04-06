from apps.common.models import BaseModel
from django.db import models
from django.contrib.auth.models import User
from apps.mandantes.models import Mandante
from django.utils import timezone


class Proyecto(BaseModel):

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_started = models.DateTimeField(default=timezone.now, blank=True)
    is_completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mandante = models.ForeignKey(Mandante, on_delete=models.CASCADE, related_name="proyectos")

    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title + ' - ' + self.mandante.name + ' by ' + str(self.user.username)
    


class Imagenes_proyecto(models.Model):
    image_url = models.URLField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"Imagen del proyecto: {self.proyecto.title}"