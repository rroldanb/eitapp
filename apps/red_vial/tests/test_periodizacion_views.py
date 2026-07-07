import json
from datetime import date, time

import pytest
from django.urls import reverse

from apps.red_vial.models import Periodizacion

pytestmark = pytest.mark.django_db


@pytest.fixture
def nodo_con_pc(proyecto):
    from apps.red_vial.models import Arco, Nodo

    nodo = Nodo.objects.create(numero=1, numero_pc=1, proyecto=proyecto)
    arco = Arco.objects.create(nodo_origen=nodo, nodo_destino=nodo, longitud=1, proyecto=proyecto)
    return nodo, arco


@pytest.fixture
def periodo(proyecto):
    from apps.red_vial.models import Periodo

    return Periodo.objects.create(
        proyecto=proyecto,
        codigo="PM-L",
        hora_inicio="07:00",
        hora_fin="09:00",
        es_laboral=True,
    )


@pytest.fixture
def pc(proyecto, nodo_con_pc):
    from apps.red_vial.models import PuntoControl

    _, arco = nodo_con_pc
    return PuntoControl.objects.create(
        nodo=nodo_con_pc[0],
        movimiento="12",
        arco_entrada=arco,
        arco_salida=arco,
        proyecto=proyecto,
    )


@pytest.fixture
def periodizacion(proyecto, pc, periodo):
    return Periodizacion.objects.create(
        fecha=date(2025, 3, 15),
        pc=pc,
        pc_mov="1>1_1>1",
        periodo=periodo,
        hora=time(8, 0),
    )


class TestPeriodizacionListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodizacion_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        tmpls = [t.name for t in response.templates]
        assert "red_vial/periodizacion_list.html" in tmpls

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodizacion_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        tmpls = [t.name for t in response.templates]
        assert "partials/Periodizacion/periodizacion_container.html" in tmpls

    def test_lists_rows(self, client, user, proyecto, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert str(periodizacion.id) in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("periodizacion_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302

    def test_filters_by_nodo(self, client, user, proyecto, pc, periodo, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, {"nodo": [pc.nodo_id]})
        assert response.status_code == 200
        assert str(periodizacion.id) in response.content.decode()

    def test_filters_by_fecha(self, client, user, proyecto, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, {"fecha": "2025-03-15"})
        assert response.status_code == 200
        assert str(periodizacion.id) in response.content.decode()


class TestPeriodizacionGenerarView:
    def test_generates_rows(self, client, user, proyecto, pc, periodo):
        from apps.red_vial.models.coeficiente_cruce import CoeficienteCruce

        CoeficienteCruce.objects.create(
            nomenclatura="VL",
            tipo_transporte="Vehículo Liviano",
            coeficiente=1.0,
            is_standard=True,
        )
        client.force_login(user)
        url = reverse("periodizacion_generar", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            json.dumps(
                {
                    "nodo_ids": [str(pc.nodo_id)],
                    "periodo_ids": [str(periodo.id)],
                    "fecha": "2025-03-15",
                    "fecha_generar": "2025-03-15",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert int(response["X-Generated-Count"]) >= 1
        assert Periodizacion.objects.filter(fecha=date(2025, 3, 15)).count() >= 1

    def test_rejects_missing_fields(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodizacion_generar", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto):
        url = reverse("periodizacion_generar", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            json.dumps({"nodo_ids": [], "periodo_ids": [], "fecha": "2025-03-15"}),
            content_type="application/json",
        )
        assert response.status_code == 302


class TestPeriodizacionUpdateView:
    def test_updates_vl(self, client, user, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_update", kwargs={"item_id": periodizacion.id})
        response = client.put(
            url,
            json.dumps({"vl": 200}),
            content_type="application/json",
        )
        assert response.status_code == 200
        periodizacion.refresh_from_db()
        assert periodizacion.vl == 200

    def test_sets_hx_trigger(self, client, user, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_update", kwargs={"item_id": periodizacion.id})
        response = client.put(
            url,
            json.dumps({"vl": 200}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_redirects_anon(self, client, periodizacion):
        url = reverse("periodizacion_update", kwargs={"item_id": periodizacion.id})
        response = client.put(
            url,
            json.dumps({"vl": 200}),
            content_type="application/json",
        )
        assert response.status_code == 302


class TestPeriodizacionDeleteView:
    def test_deletes_row(self, client, user, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_delete", kwargs={"item_id": periodizacion.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not Periodizacion.objects.filter(id=periodizacion.id).exists()

    def test_returns_204_no_content(self, client, user, periodizacion):
        client.force_login(user)
        url = reverse("periodizacion_delete", kwargs={"item_id": periodizacion.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_redirects_anon(self, client, periodizacion):
        url = reverse("periodizacion_delete", kwargs={"item_id": periodizacion.id})
        response = client.delete(url)
        assert response.status_code == 302
