import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Regulacion

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def mandante():
    return Mandante.objects.create(name="Mandante Test", location="Loc")


@pytest.fixture
def proyecto(user, mandante):
    return Proyecto.objects.create(title="Proyecto Test", user=user, mandante=mandante)


@pytest.fixture
def regulacion():
    return Regulacion.objects.create(codigo="SEM", descripcion="Semaforo")


class TestRegulacionesListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("regulaciones_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/regulaciones_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("regulaciones_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Regulaciones/regulaciones_table.html" in [
            t.name for t in response.templates
        ]

    def test_lists_regulaciones(self, client, user, proyecto, regulacion):
        client.force_login(user)
        url = reverse("regulaciones_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert regulacion.codigo in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("regulaciones_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestRegulacionCreateView:
    def test_creates_regulacion(self, client, user):
        client.force_login(user)
        url = reverse("regulacion_create")
        response = client.post(url, {"codigo": "PARE", "descripcion": "Señal de pare"})
        assert response.status_code == 200
        assert Regulacion.objects.filter(codigo="PARE").exists()
        assert "partials/Regulaciones/regulacion_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user):
        client.force_login(user)
        url = reverse("regulacion_create")
        response = client.post(url, {})
        assert response.status_code == 400

    def test_rejects_duplicate_codigo(self, client, user, regulacion):
        client.force_login(user)
        url = reverse("regulacion_create")
        response = client.post(url, {"codigo": regulacion.codigo, "descripcion": "Duplicado"})
        assert response.status_code == 400

    def test_redirects_anon(self, client):
        url = reverse("regulacion_create")
        response = client.post(url, {"codigo": "TEST", "descripcion": "Test"})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user):
        client.force_login(user)
        url = reverse("regulacion_create")
        response = client.post(url, {"codigo": "CEDA", "descripcion": "Ceda el paso"})
        assert response["HX-Trigger"] == "regulacion-created"


class TestRegulacionUpdateView:
    def test_updates_regulacion(self, client, user, regulacion):
        client.force_login(user)
        url = reverse("regulacion_update", kwargs={"item_id": regulacion.id})
        response = client.put(
            url,
            data=f"codigo={regulacion.codigo}&descripcion=Actualizada",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        regulacion.refresh_from_db()
        assert regulacion.descripcion == "Actualizada"
        assert "partials/Regulaciones/regulacion_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, regulacion):
        client.force_login(user)
        url = reverse("regulacion_update", kwargs={"item_id": regulacion.id})
        response = client.put(
            url,
            data=f"codigo={regulacion.codigo}&descripcion=X",
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_redirects_anon(self, client, regulacion):
        url = reverse("regulacion_update", kwargs={"item_id": regulacion.id})
        response = client.put(
            url,
            data="codigo=X&descripcion=X",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 302


class TestRegulacionDeleteView:
    def test_deletes_regulacion(self, client, user, regulacion):
        client.force_login(user)
        url = reverse("regulacion_delete", kwargs={"item_id": regulacion.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not Regulacion.objects.filter(id=regulacion.id).exists()

    def test_returns_204_no_content(self, client, user, regulacion):
        client.force_login(user)
        url = reverse("regulacion_delete", kwargs={"item_id": regulacion.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, regulacion):
        client.force_login(user)
        url = reverse("regulacion_delete", kwargs={"item_id": regulacion.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "regulacion-deleted"
