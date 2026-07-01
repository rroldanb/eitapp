import pytest
from django.contrib.auth.models import User
from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def mandante():
    return Mandante.objects.create(name="Mandante Test", location="Loc")


@pytest.fixture
def proyecto(user, mandante):
    return Proyecto.objects.create(
        title="Proyecto Test",
        user=user,
        mandante=mandante,
    )
