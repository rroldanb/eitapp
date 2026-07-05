import pytest
from django.urls import reverse

from apps.red_vial.models import CoeficienteCruce

pytestmark = pytest.mark.django_db


@pytest.fixture
def coeficiente_estandar():
    return CoeficienteCruce.objects.create(
        nomenclatura="VL",
        tipo_transporte="Vehículo Liviano",
        coeficiente=1.0,
        is_standard=True,
        proyecto=None,
    )


@pytest.fixture
def coeficiente_proyecto(proyecto):
    return CoeficienteCruce.objects.create(
        nomenclatura="VL",
        tipo_transporte="Vehículo Liviano",
        coeficiente=1.5,
        is_standard=False,
        proyecto=proyecto,
    )


class TestCoeficientesCruceListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("coeficientes_cruce_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/coeficientes_cruce_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("coeficientes_cruce_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/CoeficientesCruce/coeficientes_cruce_table.html" in [
            t.name for t in response.templates
        ]

    def test_lists_coeficientes(self, client, user, proyecto, coeficiente_estandar):
        client.force_login(user)
        url = reverse("coeficientes_cruce_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert coeficiente_estandar.nomenclatura in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("coeficientes_cruce_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestCoeficienteCruceCreateView:
    def test_creates_coeficiente(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_create")
        response = client.post(
            url,
            {
                "nomenclatura": "BUS",
                "tipo_transporte": "Bus",
                "coeficiente": "2.0",
                "is_standard": "false",
                "proyecto": proyecto.id,
            },
        )
        assert response.status_code == 200
        assert CoeficienteCruce.objects.filter(nomenclatura="BUS").exists()
        assert "partials/CoeficientesCruce/coeficiente_cruce_row.html" in [
            t.name for t in response.templates
        ]

    def test_rejects_empty_data(self, client, user):
        client.force_login(user)
        url = reverse("coeficiente_cruce_create")
        response = client.post(url, {})
        assert response.status_code == 400

    def test_redirects_anon(self, client):
        url = reverse("coeficiente_cruce_create")
        response = client.post(url, {"nomenclatura": "X"})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_create")
        response = client.post(
            url,
            {
                "nomenclatura": "BUS",
                "tipo_transporte": "Bus",
                "coeficiente": "2.0",
                "is_standard": "false",
                "proyecto": proyecto.id,
            },
        )
        assert response["HX-Trigger"] == "coeficiente-cruce-created"


class TestCoeficienteCruceUpdateView:
    def test_updates_coeficiente(self, client, user, coeficiente_proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_update", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.put(
            url,
            data=f"nomenclatura={coeficiente_proyecto.nomenclatura}&tipo_transporte={coeficiente_proyecto.tipo_transporte}&coeficiente=2.5&proyecto={coeficiente_proyecto.proyecto_id}",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        coeficiente_proyecto.refresh_from_db()
        assert coeficiente_proyecto.coeficiente == 2.5
        assert "partials/CoeficientesCruce/coeficiente_cruce_row.html" in [
            t.name for t in response.templates
        ]

    def test_sets_hx_trigger(self, client, user, coeficiente_proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_update", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.put(
            url,
            data=f"nomenclatura={coeficiente_proyecto.nomenclatura}&tipo_transporte={coeficiente_proyecto.tipo_transporte}&coeficiente=3.0&proyecto={coeficiente_proyecto.proyecto_id}",
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_row_contains_inputs_for_non_standard(self, client, user, coeficiente_proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_update", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.put(
            url,
            data=f"nomenclatura={coeficiente_proyecto.nomenclatura}&tipo_transporte={coeficiente_proyecto.tipo_transporte}&coeficiente=1.5&proyecto={coeficiente_proyecto.proyecto_id}",
            content_type="application/x-www-form-urlencoded",
        )
        content = response.content.decode()
        assert "field-input hidden" in content
        assert "save-row-btn hidden" in content
        assert "field-display" in content

    def test_redirects_anon(self, client, coeficiente_proyecto):
        url = reverse("coeficiente_cruce_update", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.put(
            url, data="coeficiente=1.0", content_type="application/x-www-form-urlencoded"
        )
        assert response.status_code == 302


class TestCoeficienteCruceDeleteView:
    def test_deletes_coeficiente(self, client, user, coeficiente_proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_delete", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not CoeficienteCruce.objects.filter(id=coeficiente_proyecto.id).exists()

    def test_returns_204_no_content(self, client, user, coeficiente_proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_delete", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, coeficiente_proyecto):
        client.force_login(user)
        url = reverse("coeficiente_cruce_delete", kwargs={"item_id": coeficiente_proyecto.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "coeficiente-cruce-deleted"
