from .calle_urls import urlpatterns as calle_urlpatterns
from .nodo_urls import urlpatterns as nodo_urlpatterns
from .arco_urls import urlpatterns as arco_urlpatterns
from .regulacion_urls import urlpatterns as regulacion_urlpatterns
from .punto_control_urls import urlpatterns as punto_control_urlpatterns
from .coeficiente_cruce_urls import urlpatterns as coeficiente_cruce_urlpatterns
from .all_urls import urlpatterns as all_urlpatterns
urlpatterns = calle_urlpatterns + nodo_urlpatterns + arco_urlpatterns + regulacion_urlpatterns + punto_control_urlpatterns + coeficiente_cruce_urlpatterns + all_urlpatterns