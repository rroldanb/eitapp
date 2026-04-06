"""
URL configuration for transito_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


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
