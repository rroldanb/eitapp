import pytest
from django.urls import reverse
from apps.red_vial.models.transyt import FaseSemaforica
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
def fase(proyecto, punto_control):
    return FaseSemaforica.objects.create(
        proyecto=proyecto, punto_control=punto_control,
        fase_numero=1, verde_inicio=10.0, verde_fin=30.0,
    )


class TestFaseSemaforicaListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("fases_semaforicas_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/fases_semaforicas_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("fases_semaforicas_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Transyt/fase_semaforica_table.html" in [t.name for t in response.templates]

    def test_lists_fases(self, client, user, proyecto, fase):
        client.force_login(user)
        url = reverse("fases_semaforicas_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert str(fase.fase_numero) in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("fases_semaforicas_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestFaseSemaforicaCreateView:
    def test_creates_fase(self, client, user, proyecto, punto_control):
        client.force_login(user)
        url = reverse("fase_semaforica_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {
            "punto_control": punto_control.id,
            "fase_numero": "2",
            "verde_inicio": "15.0",
            "verde_fin": "35.0",
        })
        assert response.status_code == 200
        assert FaseSemaforica.objects.filter(proyecto=proyecto, fase_numero=2).exists()
        assert "partials/Transyt/fase_semaforica_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("fase_semaforica_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto, punto_control):
        url = reverse("fase_semaforica_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"punto_control": punto_control.id})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto, punto_control):
        client.force_login(user)
        url = reverse("fase_semaforica_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {
            "punto_control": punto_control.id,
            "fase_numero": "2",
            "verde_inicio": "10.0",
            "verde_fin": "30.0",
        })
        assert response["HX-Trigger"] == "fase-semaforica-created"


class TestFaseSemaforicaUpdateView:
    def _put_data(self, fase, **kwargs):
        params = {
            "punto_control": fase.punto_control_id,
            "fase_numero": fase.fase_numero,
            "verde_inicio": fase.verde_inicio,
            "verde_fin": fase.verde_fin,
        }
        params.update(kwargs)
        return "&".join(f"{k}={v}" for k, v in params.items())

    def test_updates_fase(self, client, user, fase):
        client.force_login(user)
        url = reverse("fase_semaforica_update", kwargs={"item_id": fase.id})
        response = client.put(
            url,
            data=self._put_data(fase, verde_inicio=20.0, verde_fin=40.0),
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        fase.refresh_from_db()
        assert fase.verde_inicio == 20.0
        assert "partials/Transyt/fase_semaforica_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, fase):
        client.force_login(user)
        url = reverse("fase_semaforica_update", kwargs={"item_id": fase.id})
        response = client.put(
            url,
            data=self._put_data(fase),
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_row_contains_inputs(self, client, user, fase):
        client.force_login(user)
        url = reverse("fase_semaforica_update", kwargs={"item_id": fase.id})
        response = client.put(
            url,
            data=self._put_data(fase),
            content_type="application/x-www-form-urlencoded",
        )
        content = response.content.decode()
        assert 'field-input hidden' in content
        assert 'save-row-btn hidden' in content
        assert 'field-display' in content

    def test_redirects_anon(self, client, fase):
        url = reverse("fase_semaforica_update", kwargs={"item_id": fase.id})
        response = client.put(
            url, data=f"punto_control={fase.punto_control_id}&verde_inicio=20.0",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 302


class TestFaseSemaforicaDeleteView:
    def test_deletes_fase(self, client, user, fase):
        client.force_login(user)
        url = reverse("fase_semaforica_delete", kwargs={"item_id": fase.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not FaseSemaforica.objects.filter(id=fase.id).exists()

    def test_returns_204_no_content(self, client, user, fase):
        client.force_login(user)
        url = reverse("fase_semaforica_delete", kwargs={"item_id": fase.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, fase):
        client.force_login(user)
        url = reverse("fase_semaforica_delete", kwargs={"item_id": fase.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "fase-semaforica-deleted"
