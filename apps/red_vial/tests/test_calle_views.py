import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Calle


pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def mandante():
    return Mandante.objects.create(name="Mandante Test", location="Loc")


@pytest.fixture
def proyecto(user, mandante):
    return Proyecto.objects.create(
        title="Proyecto Test", user=user, mandante=mandante,
    )


@pytest.fixture
def calle(proyecto):
    return Calle.objects.create(numero=1, nombre="Calle Uno", proyecto=proyecto)


class TestCalleListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/calles_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Calles/calles_table.html" in [t.name for t in response.templates]

    def test_lists_calles(self, client, user, proyecto, calle):
        client.force_login(user)
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert calle.nombre in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestCalleCreateView:
    def test_creates_calle(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("calle_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": 2, "nombre": "Calle Dos"})
        assert response.status_code == 200
        assert Calle.objects.filter(proyecto=proyecto, numero=2).exists()
        assert "partials/Calles/calle_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("calle_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400
        assert "partials/Calles/calle_create.html" in [t.name for t in response.templates]

    def test_rejects_duplicate_numero(self, client, user, proyecto, calle):
        client.force_login(user)
        url = reverse("calle_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": calle.numero, "nombre": "Otra"})
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto):
        url = reverse("calle_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": 1, "nombre": "X"})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("calle_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"numero": 2, "nombre": "Calle Nueva"})
        assert response["HX-Trigger"] == "calle-created"


class TestCalleUpdateView:
    def test_updates_calle(self, client, user, calle):
        client.force_login(user)
        url = reverse("calle_update", kwargs={"item_id": calle.id})
        response = client.put(
            url,
            data=f"numero={calle.numero}&nombre=Calle Actualizada",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        calle.refresh_from_db()
        assert calle.nombre == "Calle Actualizada"
        assert "partials/Calles/calle_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, calle):
        client.force_login(user)
        url = reverse("calle_update", kwargs={"item_id": calle.id})
        response = client.put(
            url,
            data=f"numero={calle.numero}&nombre=Calle X",
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_calle_row_contains_inputs(self, client, user, calle):
        client.force_login(user)
        url = reverse("calle_update", kwargs={"item_id": calle.id})
        response = client.put(
            url,
            data=f"numero={calle.numero}&nombre=Calle X",
            content_type="application/x-www-form-urlencoded",
        )
        content = response.content.decode()
        assert 'field-input hidden' in content
        assert 'save-row-btn hidden' in content
        assert 'field-display' in content

    def test_redirects_anon(self, client, calle):
        url = reverse("calle_update", kwargs={"item_id": calle.id})
        response = client.put(url, data="numero=1&nombre=X", content_type="application/x-www-form-urlencoded")
        assert response.status_code == 302


class TestCalleDeleteView:
    def test_deletes_calle(self, client, user, calle):
        client.force_login(user)
        url = reverse("calle_delete", kwargs={"item_id": calle.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not Calle.objects.filter(id=calle.id).exists()

    def test_returns_204_no_content(self, client, user, calle):
        client.force_login(user)
        url = reverse("calle_delete", kwargs={"item_id": calle.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, calle):
        client.force_login(user)
        url = reverse("calle_delete", kwargs={"item_id": calle.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "calle-deleted"


class TestCallePagination:
    def test_paginate_by_default(self, client, user, proyecto):
        client.force_login(user)
        for i in range(60):
            Calle.objects.create(numero=i + 10, nombre=f"Calle {i}", proyecto=proyecto)
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "Página 1 de 3" in response.content.decode()

    def test_second_page(self, client, user, proyecto):
        client.force_login(user)
        for i in range(60):
            Calle.objects.create(numero=i + 10, nombre=f"Calle {i}", proyecto=proyecto)
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, {"page": 2})
        assert response.status_code == 200
        assert "Página 2 de 3" in response.content.decode()

    def test_htmx_partial_has_pagination(self, client, user, proyecto):
        client.force_login(user)
        for i in range(25):
            Calle.objects.create(numero=i + 10, nombre=f"Calle {i}", proyecto=proyecto)
        url = reverse("calles_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, {"page": 2}, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "Página 2 de 2" in response.content.decode()
