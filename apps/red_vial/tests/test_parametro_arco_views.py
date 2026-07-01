import pytest
from django.urls import reverse
from apps.red_vial.models.transyt import ParametroArco
from apps.red_vial.models import PuntoControl, Nodo


pytestmark = pytest.mark.django_db


@pytest.fixture
def nodo(proyecto):
    return Nodo.objects.create(numero=1, proyecto=proyecto)


@pytest.fixture
def arco(proyecto, nodo):
    from apps.red_vial.models import Arco
    return Arco.objects.create(
        nodo_origen=nodo, nodo_destino=nodo,
        proyecto=proyecto, longitud=100,
    )


@pytest.fixture
def punto_control(proyecto, nodo, arco):
    return PuntoControl.objects.create(
        proyecto=proyecto, nodo=nodo, movimiento='12',
        arco_entrada=arco, arco_salida=arco,
    )


@pytest.fixture
def parametro_arco(proyecto, punto_control):
    return ParametroArco.objects.create(
        proyecto=proyecto, punto_control=punto_control,
        flujo_saturacion=1800, ponderador_demora=1.0,
        ponderador_detencion=1.0,
    )


class TestParametroArcoListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("parametros_arco_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/parametros_arco_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("parametros_arco_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Transyt/parametro_arco_table.html" in [t.name for t in response.templates]

    def test_lists_parametros(self, client, user, proyecto, parametro_arco):
        client.force_login(user)
        url = reverse("parametros_arco_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert str(parametro_arco.flujo_saturacion) in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("parametros_arco_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestParametroArcoCreateView:
    def test_creates_parametro(self, client, user, proyecto, punto_control):
        client.force_login(user)
        url = reverse("parametro_arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {
            "punto_control": punto_control.id,
            "flujo_saturacion": "2000",
            "ponderador_demora": "1.5",
            "ponderador_detencion": "0.8",
        })
        assert response.status_code == 200
        assert ParametroArco.objects.filter(proyecto=proyecto).exists()
        assert "partials/Transyt/parametro_arco_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("parametro_arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto, punto_control):
        url = reverse("parametro_arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"punto_control": punto_control.id})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto, punto_control):
        client.force_login(user)
        url = reverse("parametro_arco_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {
            "punto_control": punto_control.id,
            "flujo_saturacion": "2000",
            "ponderador_demora": "1.0",
            "ponderador_detencion": "1.0",
        })
        assert response["HX-Trigger"] == "parametro-arco-created"


class TestParametroArcoUpdateView:
    def _put_data(self, parametro_arco, **kwargs):
        params = {
            "punto_control": parametro_arco.punto_control_id,
            "flujo_saturacion": parametro_arco.flujo_saturacion,
            "ponderador_demora": parametro_arco.ponderador_demora,
            "ponderador_detencion": parametro_arco.ponderador_detencion,
        }
        params.update(kwargs)
        return "&".join(f"{k}={v}" for k, v in params.items())

    def test_updates_parametro(self, client, user, parametro_arco):
        client.force_login(user)
        url = reverse("parametro_arco_update", kwargs={"item_id": parametro_arco.id})
        response = client.put(
            url,
            data=self._put_data(parametro_arco, flujo_saturacion=2200, ponderador_demora=1.2, ponderador_detencion=0.9),
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        parametro_arco.refresh_from_db()
        assert parametro_arco.flujo_saturacion == 2200
        assert "partials/Transyt/parametro_arco_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, parametro_arco):
        client.force_login(user)
        url = reverse("parametro_arco_update", kwargs={"item_id": parametro_arco.id})
        response = client.put(
            url,
            data=self._put_data(parametro_arco),
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_row_contains_inputs(self, client, user, parametro_arco):
        client.force_login(user)
        url = reverse("parametro_arco_update", kwargs={"item_id": parametro_arco.id})
        response = client.put(
            url,
            data=self._put_data(parametro_arco),
            content_type="application/x-www-form-urlencoded",
        )
        content = response.content.decode()
        assert 'field-input hidden' in content
        assert 'save-row-btn hidden' in content
        assert 'field-display' in content

    def test_redirects_anon(self, client, parametro_arco):
        url = reverse("parametro_arco_update", kwargs={"item_id": parametro_arco.id})
        response = client.put(
            url, data=f"punto_control={parametro_arco.punto_control_id}&flujo_saturacion=2000",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 302


class TestParametroArcoDeleteView:
    def test_deletes_parametro(self, client, user, parametro_arco):
        client.force_login(user)
        url = reverse("parametro_arco_delete", kwargs={"item_id": parametro_arco.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not ParametroArco.objects.filter(id=parametro_arco.id).exists()

    def test_returns_204_no_content(self, client, user, parametro_arco):
        client.force_login(user)
        url = reverse("parametro_arco_delete", kwargs={"item_id": parametro_arco.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, parametro_arco):
        client.force_login(user)
        url = reverse("parametro_arco_delete", kwargs={"item_id": parametro_arco.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "parametro-arco-deleted"
