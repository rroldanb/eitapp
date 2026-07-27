from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly
from apps.proyectos.models.proyecto import Proyecto

from .serializers.proyecto import ProyectoSerializer


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.select_related("mandante", "user").all()
    serializer_class = ProyectoSerializer
    permission_classes = [IsAdminOrReadOnly]
