import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Calle, Nodo

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
def calle(proyecto):
    return Calle.objects.create(numero=1, nombre="Calle Uno", proyecto=proyecto)


@pytest.fixture
def nodo(proyecto):
    return Nodo.objects.create(numero=1, interseccion="Test Intersection", proyecto=proyecto)


class TestNodosListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("nodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/nodos_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("nodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Nodos/nodos_table.html" in [t.name for t in response.templates]

    def test_lists_nodos(self, client, user, proyecto, nodo):
        client.force_login(user)
        url = reverse("nodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert str(nodo.numero) in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("nodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302

    def test_paginate_by_default(self, client, user, proyecto):
        client.force_login(user)
        for i in range(25):
            Nodo.objects.create(numero=i + 10, proyecto=proyecto)
        url = reverse("nodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200


class TestNodoCreateView:
    def test_creates_nodo(self, client, user, proyecto, calle):
        client.force_login(user)
        url = reverse("nodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {"numero": 2, "interseccion": "Nueva Interseccion", "calle_1": calle.id},
        )
        assert response.status_code == 200
        assert Nodo.objects.filter(proyecto=proyecto, numero=2).exists()
        assert "partials/Nodos/nodo_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("nodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400

    def test_rejects_duplicate_numero(self, client, user, proyecto, nodo):
        client.force_login(user)
        url = reverse("nodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": nodo.numero})
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto):
        url = reverse("nodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": 1})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("nodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": 5})
        assert response["HX-Trigger"] == "nodo-created"


class TestNodoUpdateView:
    def test_updates_nodo(self, client, user, nodo):
        client.force_login(user)
        url = reverse("nodo_update", kwargs={"item_id": nodo.id})
        response = client.put(
            url,
            data=f"numero={nodo.numero}&interseccion=Actualizada",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        nodo.refresh_from_db()
        assert nodo.interseccion == "Actualizada"
        assert "partials/Nodos/nodo_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, nodo):
        client.force_login(user)
        url = reverse("nodo_update", kwargs={"item_id": nodo.id})
        response = client.put(
            url,
            data=f"numero={nodo.numero}&interseccion=X",
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_nodo_row_contains_inputs(self, client, user, nodo):
        client.force_login(user)
        url = reverse("nodo_update", kwargs={"item_id": nodo.id})
        response = client.put(
            url,
            data=f"numero={nodo.numero}&interseccion=X",
            content_type="application/x-www-form-urlencoded",
        )
        content = response.content.decode()
        assert "field-input hidden" in content
        assert "save-row-btn hidden" in content
        assert "field-display" in content

    def test_redirects_anon(self, client, nodo):
        url = reverse("nodo_update", kwargs={"item_id": nodo.id})
        response = client.put(
            url,
            data="numero=1&interseccion=X",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 302


class TestNodoDeleteView:
    def test_deletes_nodo(self, client, user, nodo):
        client.force_login(user)
        url = reverse("nodo_delete", kwargs={"item_id": nodo.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not Nodo.objects.filter(id=nodo.id).exists()

    def test_returns_204_no_content(self, client, user, nodo):
        client.force_login(user)
        url = reverse("nodo_delete", kwargs={"item_id": nodo.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, nodo):
        client.force_login(user)
        url = reverse("nodo_delete", kwargs={"item_id": nodo.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "nodo-deleted"
