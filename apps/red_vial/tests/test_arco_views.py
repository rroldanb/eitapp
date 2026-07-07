import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Arco, Nodo

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
def nodo_origen(proyecto):
    return Nodo.objects.create(numero=1, proyecto=proyecto)


@pytest.fixture
def nodo_destino(proyecto):
    return Nodo.objects.create(numero=2, proyecto=proyecto)


@pytest.fixture
def arco(proyecto, nodo_origen, nodo_destino):
    return Arco.objects.create(
        nodo_origen=nodo_origen,
        nodo_destino=nodo_destino,
        longitud=150.0,
        proyecto=proyecto,
    )


class TestArcosListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("arcos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/arcos_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("arcos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Arcos/arcos_table.html" in [t.name for t in response.templates]

    def test_lists_arcos(self, client, user, proyecto, arco):
        client.force_login(user)
        url = reverse("arcos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert str(arco.nodo_origen.numero) in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("arcos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestArcoCreateView:
    def test_creates_arco(self, client, user, proyecto, nodo_origen, nodo_destino):
        client.force_login(user)
        url = reverse("arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {"nodo_origen": nodo_origen.id, "nodo_destino": nodo_destino.id, "longitud": 200.0},
        )
        assert response.status_code == 200
        assert Arco.objects.filter(proyecto=proyecto, longitud=200.0).exists()
        assert "partials/Arcos/arco_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400

    def test_rejects_same_node(self, client, user, proyecto, nodo_origen):
        client.force_login(user)
        url = reverse("arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {"nodo_origen": nodo_origen.id, "nodo_destino": nodo_origen.id, "longitud": 100.0},
        )
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto):
        url = reverse("arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"nodo_origen": "", "nodo_destino": "", "longitud": 100.0})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto, nodo_origen, nodo_destino):
        client.force_login(user)
        url = reverse("arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {"nodo_origen": nodo_origen.id, "nodo_destino": nodo_destino.id, "longitud": 300.0},
        )
        assert response["HX-Trigger"] == "arco-created"


class TestArcoUpdateView:
    def test_updates_arco(self, client, user, arco):
        client.force_login(user)
        url = reverse("arco_update", kwargs={"item_id": arco.id})
        response = client.put(
            url,
            data=f"nodo_origen={arco.nodo_origen_id}&nodo_destino={arco.nodo_destino_id}&longitud=999.0",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        arco.refresh_from_db()
        assert arco.longitud == 999.0
        assert "partials/Arcos/arco_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, arco):
        client.force_login(user)
        url = reverse("arco_update", kwargs={"item_id": arco.id})
        response = client.put(
            url,
            data=f"nodo_origen={arco.nodo_origen_id}&nodo_destino={arco.nodo_destino_id}&longitud=500.0",
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_redirects_anon(self, client, arco):
        url = reverse("arco_update", kwargs={"item_id": arco.id})
        response = client.put(
            url,
            data=f"nodo_origen={arco.nodo_origen_id}&nodo_destino={arco.nodo_destino_id}&longitud=100.0",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 302


class TestArcoDeleteView:
    def test_deletes_arco(self, client, user, arco):
        client.force_login(user)
        url = reverse("arco_delete", kwargs={"item_id": arco.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not Arco.objects.filter(id=arco.id).exists()

    def test_returns_204_no_content(self, client, user, arco):
        client.force_login(user)
        url = reverse("arco_delete", kwargs={"item_id": arco.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, arco):
        client.force_login(user)
        url = reverse("arco_delete", kwargs={"item_id": arco.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "arco-deleted"
