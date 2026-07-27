from rest_framework.routers import DefaultRouter

from apps.mandantes.api import ContactoViewSet, MandanteViewSet
from apps.proyectos.api import ProyectoViewSet
from apps.red_vial.api import (
    ArcoViewSet,
    CalleViewSet,
    CoeficienteCruceViewSet,
    ConfiguracionTransytViewSet,
    FaseSemaforicaViewSet,
    NodoViewSet,
    ParametroArcoViewSet,
    PeriodizacionViewSet,
    PeriodoViewSet,
    PuntoControlViewSet,
    RegulacionViewSet,
    ResumenFlujoViewSet,
)
from apps.tasks.api import TaskViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, "task")
router.register(r"mandantes", MandanteViewSet, "mandante")
router.register(r"contactos", ContactoViewSet, "contacto")
router.register(r"proyectos", ProyectoViewSet, "proyecto")
router.register(r"calles", CalleViewSet, "calle")
router.register(r"nodos", NodoViewSet, "nodo")
router.register(r"arcos", ArcoViewSet, "arco")
router.register(r"regulaciones", RegulacionViewSet, "regulacion")
router.register(r"coeficientes-cruce", CoeficienteCruceViewSet, "coeficiente_cruce")
router.register(r"puntos-control", PuntoControlViewSet, "punto_control")
router.register(r"periodos", PeriodoViewSet, "periodo")
router.register(r"periodizaciones", PeriodizacionViewSet, "periodizacion")
router.register(r"resumenes-flujo", ResumenFlujoViewSet, "resumen_flujo")
router.register(r"configuraciones-transyt", ConfiguracionTransytViewSet, "configuracion_transyt")
router.register(r"parametros-arco", ParametroArcoViewSet, "parametro_arco")
router.register(r"fases-semaforicas", FaseSemaforicaViewSet, "fase_semaforica")

urlpatterns = router.urls
