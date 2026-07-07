import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Arco, Nodo, PuntoControl

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
def nodo(proyecto):
    return Nodo.objects.create(numero=1, proyecto=proyecto, numero_pc=1)


@pytest.fixture
def nodo_destino(proyecto):
    return Nodo.objects.create(numero=2, proyecto=proyecto)


@pytest.fixture
def arco_entrada(proyecto, nodo, nodo_destino):
    return Arco.objects.create(
        nodo_origen=nodo_destino, nodo_destino=nodo, longitud=100.0, proyecto=proyecto
    )


@pytest.fixture
def arco_salida(proyecto, nodo, nodo_destino):
    return Arco.objects.create(
        nodo_origen=nodo, nodo_destino=nodo_destino, longitud=100.0, proyecto=proyecto
    )


@pytest.fixture
def punto_control(proyecto, nodo, arco_entrada, arco_salida):
    return PuntoControl.objects.create(
        nodo=nodo,
        movimiento="12",
        proyecto=proyecto,
        arco_entrada=arco_entrada,
        arco_salida=arco_salida,
    )


class TestPuntosControlListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("puntos_control_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/puntos_control_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("puntos_control_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/PuntosControl/puntos_control_table.html" in [
            t.name for t in response.templates
        ]

    def test_lists_puntos_control(self, client, user, proyecto, punto_control):
        client.force_login(user)
        url = reverse("puntos_control_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert punto_control.movimiento in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("puntos_control_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestPuntoControlCreateView:
    def test_creates_punto_control(self, client, user, proyecto, nodo, arco_entrada, arco_salida):
        client.force_login(user)
        url = reverse("punto_control_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {
                "nodo": nodo.id,
                "movimiento": "21",
                "arco_entrada": arco_entrada.id,
                "arco_salida": arco_salida.id,
                "is_prioritario": False,
            },
        )
        assert response.status_code == 200
        assert PuntoControl.objects.filter(proyecto=proyecto, movimiento="21").exists()
        assert "partials/PuntosControl/punto_control_row.html" in [
            t.name for t in response.templates
        ]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("punto_control_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto):
        url = reverse("punto_control_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"nodo": "", "movimiento": "12"})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(
        self, client, user, proyecto, nodo, arco_entrada, arco_salida
    ):
        client.force_login(user)
        url = reverse("punto_control_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {
                "nodo": nodo.id,
                "movimiento": "13",
                "arco_entrada": arco_entrada.id,
                "arco_salida": arco_salida.id,
                "is_prioritario": True,
            },
        )
        assert response["HX-Trigger"] == "punto-control-created"


class TestPuntoControlUpdateView:
    def test_updates_punto_control(self, client, user, punto_control, arco_entrada, arco_salida):
        client.force_login(user)
        url = reverse("punto_control_update", kwargs={"item_id": punto_control.id})
        response = client.put(
            url,
            data=(
                f"nodo={punto_control.nodo_id}"
                f"&movimiento={punto_control.movimiento}"
                f"&arco_entrada={arco_entrada.id}"
                f"&arco_salida={arco_salida.id}"
                f"&is_prioritario=False"
            ),
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        assert "partials/PuntosControl/punto_control_row.html" in [
            t.name for t in response.templates
        ]

    def test_sets_hx_trigger(self, client, user, punto_control, arco_entrada, arco_salida):
        client.force_login(user)
        url = reverse("punto_control_update", kwargs={"item_id": punto_control.id})
        response = client.put(
            url,
            data=(
                f"nodo={punto_control.nodo_id}"
                f"&movimiento={punto_control.movimiento}"
                f"&arco_entrada={arco_entrada.id}"
                f"&arco_salida={arco_salida.id}"
                f"&is_prioritario=False"
            ),
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_redirects_anon(self, client, punto_control):
        url = reverse("punto_control_update", kwargs={"item_id": punto_control.id})
        response = client.put(
            url,
            data="movimiento=12&is_prioritario=False",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 302


class TestPuntoControlDeleteView:
    def test_deletes_punto_control(self, client, user, punto_control):
        client.force_login(user)
        url = reverse("punto_control_delete", kwargs={"item_id": punto_control.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not PuntoControl.objects.filter(id=punto_control.id).exists()

    def test_returns_204_no_content(self, client, user, punto_control):
        client.force_login(user)
        url = reverse("punto_control_delete", kwargs={"item_id": punto_control.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, punto_control):
        client.force_login(user)
        url = reverse("punto_control_delete", kwargs={"item_id": punto_control.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "punto-control-deleted"
