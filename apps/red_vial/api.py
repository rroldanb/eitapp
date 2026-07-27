from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly
from apps.red_vial.models import (
    Arco,
    Calle,
    CoeficienteCruce,
    ConfiguracionTransyt,
    FaseSemaforica,
    Nodo,
    ParametroArco,
    Periodizacion,
    Periodo,
    PuntoControl,
    Regulacion,
    ResumenFlujo,
)

from .serializers.red_vial import (
    ArcoSerializer,
    CalleSerializer,
    CoeficienteCruceSerializer,
    ConfiguracionTransytSerializer,
    FaseSemaforicaSerializer,
    NodoSerializer,
    ParametroArcoSerializer,
    PeriodizacionSerializer,
    PeriodoSerializer,
    PuntoControlSerializer,
    RegulacionSerializer,
    ResumenFlujoSerializer,
)


class CalleViewSet(viewsets.ModelViewSet):
    queryset = Calle.objects.select_related("proyecto").all()
    serializer_class = CalleSerializer
    permission_classes = [IsAdminOrReadOnly]


class NodoViewSet(viewsets.ModelViewSet):
    queryset = Nodo.objects.select_related("proyecto", "calle_1", "calle_2").all()
    serializer_class = NodoSerializer
    permission_classes = [IsAdminOrReadOnly]


class ArcoViewSet(viewsets.ModelViewSet):
    queryset = Arco.objects.select_related("nodo_origen", "nodo_destino", "proyecto").all()
    serializer_class = ArcoSerializer
    permission_classes = [IsAdminOrReadOnly]


class RegulacionViewSet(viewsets.ModelViewSet):
    queryset = Regulacion.objects.all()
    serializer_class = RegulacionSerializer
    permission_classes = [IsAdminOrReadOnly]


class CoeficienteCruceViewSet(viewsets.ModelViewSet):
    queryset = CoeficienteCruce.objects.select_related("proyecto").all()
    serializer_class = CoeficienteCruceSerializer
    permission_classes = [IsAdminOrReadOnly]


class PuntoControlViewSet(viewsets.ModelViewSet):
    queryset = PuntoControl.objects.select_related(
        "proyecto", "nodo", "arco_entrada", "arco_salida", "regulacion"
    ).all()
    serializer_class = PuntoControlSerializer
    permission_classes = [IsAdminOrReadOnly]


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.select_related("proyecto").all()
    serializer_class = PeriodoSerializer
    permission_classes = [IsAdminOrReadOnly]


class PeriodizacionViewSet(viewsets.ModelViewSet):
    queryset = Periodizacion.objects.select_related("pc", "periodo").all()
    serializer_class = PeriodizacionSerializer
    permission_classes = [IsAdminOrReadOnly]


class ResumenFlujoViewSet(viewsets.ModelViewSet):
    queryset = ResumenFlujo.objects.select_related("pc", "periodo").all()
    serializer_class = ResumenFlujoSerializer
    permission_classes = [IsAdminOrReadOnly]


class ConfiguracionTransytViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionTransyt.objects.select_related("proyecto").all()
    serializer_class = ConfiguracionTransytSerializer
    permission_classes = [IsAdminOrReadOnly]


class ParametroArcoViewSet(viewsets.ModelViewSet):
    queryset = ParametroArco.objects.select_related("proyecto", "punto_control").all()
    serializer_class = ParametroArcoSerializer
    permission_classes = [IsAdminOrReadOnly]


class FaseSemaforicaViewSet(viewsets.ModelViewSet):
    queryset = FaseSemaforica.objects.select_related("proyecto", "punto_control").all()
    serializer_class = FaseSemaforicaSerializer
    permission_classes = [IsAdminOrReadOnly]
