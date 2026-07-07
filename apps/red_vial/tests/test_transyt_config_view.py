import pytest
from django.urls import reverse

from apps.red_vial.models import ConfiguracionTransyt

pytestmark = pytest.mark.django_db


class TestConfiguracionTransytView:
    def test_get_renders_form(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/configuracion_transyt.html" in [t.name for t in response.templates]

    def test_get_creates_default_config(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        client.get(url)
        assert ConfiguracionTransyt.objects.filter(proyecto=proyecto).exists()

    def test_get_uses_existing_config(self, client, user, proyecto):
        ConfiguracionTransyt.objects.create(
            proyecto=proyecto,
            ciclo=90,
            W=15.0,
            K=0.8,
            perdida_inicial=3.0,
            ganancia_final=2.0,
        )
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "90" in response.content.decode()

    def test_post_saves_form(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {
                "ciclo": 90,
                "W": 15.0,
                "K": 0.8,
                "perdida_inicial": 3.0,
                "ganancia_final": 2.0,
            },
        )
        assert response.status_code == 200
        config = ConfiguracionTransyt.objects.get(proyecto=proyecto)
        assert config.ciclo == 90

    def test_post_shows_saved_flag(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {
                "ciclo": 60,
                "W": 10.0,
                "K": 0.5,
                "perdida_inicial": 2.0,
                "ganancia_final": 1.0,
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "guardada" in content

    def test_post_rejects_invalid_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"ciclo": -1})
        assert response.status_code == 400

    def test_post_updates_existing_config(self, client, user, proyecto):
        ConfiguracionTransyt.objects.create(proyecto=proyecto, ciclo=60)
        client.force_login(user)
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        client.post(
            url,
            {
                "ciclo": 120,
                "W": 10.0,
                "K": 0.5,
                "perdida_inicial": 2.0,
                "ganancia_final": 1.0,
            },
        )
        config = ConfiguracionTransyt.objects.get(proyecto=proyecto)
        assert config.ciclo == 120

    def test_redirects_anon(self, client, proyecto):
        url = reverse("configuracion_transyt", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302
