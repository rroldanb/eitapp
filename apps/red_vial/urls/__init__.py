from .calle_urls import urlpatterns as calle_urlpatterns
from .nodo_urls import urlpatterns as nodo_urlpatterns
from .arco_urls import urlpatterns as arco_urlpatterns
from .regulacion_urls import urlpatterns as regulacion_urlpatterns
from .punto_control_urls import urlpatterns as punto_control_urlpatterns
from .coeficiente_cruce_urls import urlpatterns as coeficiente_cruce_urlpatterns
from .periodo_urls import urlpatterns as periodo_urlpatterns
from .periodizacion_urls import urlpatterns as periodizacion_urlpatterns
from .analisis_flujos_urls import urlpatterns as analisis_flujos_urlpatterns
from .all_urls import urlpatterns as all_urlpatterns
from .transyt_urls import urlpatterns as transyt_urlpatterns
from .import_urls import urlpatterns as import_urlpatterns
urlpatterns = calle_urlpatterns + nodo_urlpatterns + arco_urlpatterns + regulacion_urlpatterns + punto_control_urlpatterns + coeficiente_cruce_urlpatterns + periodo_urlpatterns + periodizacion_urlpatterns + analisis_flujos_urlpatterns + all_urlpatterns + transyt_urlpatterns + import_urlpatterns