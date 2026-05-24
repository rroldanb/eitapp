from django.contrib import admin
from django.urls import path, include
from apps.usuarios import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('signup/', user_views.signup, name='signup'),
    path('logout/', user_views.signout, name='signout'),
    path('signin/', user_views.signin, name='signin'),



    path('tasks/', include('apps.tasks.urls')),
    path('mandantes/', include('apps.mandantes.urls')),
    path('proyectos/', include('apps.proyectos.urls')),
    path('red-vial/', include('apps.red_vial.urls')),
]
