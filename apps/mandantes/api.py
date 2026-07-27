from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly
from apps.mandantes.models.mandante import Contacto, Mandante

from .serializers.mandante import ContactoSerializer, MandanteSerializer


class MandanteViewSet(viewsets.ModelViewSet):
    queryset = Mandante.objects.all()
    serializer_class = MandanteSerializer
    permission_classes = [IsAdminOrReadOnly]


class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.select_related("mandante").all()
    serializer_class = ContactoSerializer
    permission_classes = [IsAdminOrReadOnly]
