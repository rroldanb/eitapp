import pytest
from django.urls import reverse

from apps.red_vial.models import Periodo

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo(proyecto):
    return Periodo.objects.create(
        proyecto=proyecto,
        codigo="PM-L",
        hora_inicio="08:00",
        hora_fin="09:00",
        es_laboral=True,
    )


class TestPeriodoListView:
    def test_returns_full_template(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "red_vial/periodo_list.html" in [t.name for t in response.templates]

    def test_returns_partial_for_htmx(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "partials/Periodo/periodo_table.html" in [t.name for t in response.templates]

    def test_lists_periodos(self, client, user, proyecto, periodo):
        client.force_login(user)
        url = reverse("periodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 200
        assert periodo.get_codigo_display() in response.content.decode()

    def test_redirects_anon(self, client, proyecto):
        url = reverse("periodos_list", kwargs={"proyecto_id": proyecto.id})
        response = client.get(url)
        assert response.status_code == 302


class TestPeriodoCreateView:
    def test_creates_periodo(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {
                "codigo": "PM-L",
                "hora_inicio": "08:00",
                "hora_fin": "09:00",
                "es_laboral": "true",
            },
        )
        assert response.status_code == 200
        assert Periodo.objects.filter(proyecto=proyecto, codigo="PM-L").exists()
        assert "partials/Periodo/periodo_row.html" in [t.name for t in response.templates]

    def test_rejects_empty_data(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {})
        assert response.status_code == 400
        assert "partials/Periodo/periodo_create.html" in [t.name for t in response.templates]

    def test_rejects_duplicate_codigo(self, client, user, proyecto, periodo):
        client.force_login(user)
        url = reverse("periodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"codigo": "PM-L"})
        assert response.status_code == 400

    def test_redirects_anon(self, client, proyecto):
        url = reverse("periodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(url, {"codigo": "PM-L"})
        assert response.status_code == 302

    def test_sets_hx_trigger_on_create(self, client, user, proyecto):
        client.force_login(user)
        url = reverse("periodo_create", kwargs={"proyecto_id": proyecto.id})
        response = client.post(
            url,
            {
                "codigo": "PM-L",
                "hora_inicio": "08:00",
                "hora_fin": "09:00",
                "es_laboral": "true",
            },
        )
        assert response["HX-Trigger"] == "periodo-created"


class TestPeriodoUpdateView:
    def test_updates_periodo(self, client, user, periodo):
        client.force_login(user)
        url = reverse("periodo_update", kwargs={"item_id": periodo.id})
        response = client.put(
            url,
            data=f"codigo={periodo.codigo}&hora_inicio=10:00&hora_fin=11:00&es_laboral=true",
            content_type="application/x-www-form-urlencoded",
        )
        assert response.status_code == 200
        periodo.refresh_from_db()
        assert str(periodo.hora_inicio) == "10:00:00"
        assert "partials/Periodo/periodo_row.html" in [t.name for t in response.templates]

    def test_sets_hx_trigger(self, client, user, periodo):
        client.force_login(user)
        url = reverse("periodo_update", kwargs={"item_id": periodo.id})
        response = client.put(
            url,
            data=f"codigo={periodo.codigo}&hora_inicio=10:00&hora_fin=11:00&es_laboral=true",
            content_type="application/x-www-form-urlencoded",
        )
        assert response["HX-Trigger"] == "item-updated"

    def test_periodo_row_contains_inputs(self, client, user, periodo):
        client.force_login(user)
        url = reverse("periodo_update", kwargs={"item_id": periodo.id})
        response = client.put(
            url,
            data=f"codigo={periodo.codigo}&hora_inicio=10:00&hora_fin=11:00&es_laboral=true",
            content_type="application/x-www-form-urlencoded",
        )
        content = response.content.decode()
        assert "field-input hidden" in content
        assert "save-row-btn hidden" in content
        assert "field-display" in content

    def test_redirects_anon(self, client, periodo):
        url = reverse("periodo_update", kwargs={"item_id": periodo.id})
        response = client.put(
            url, data="codigo=PM-L", content_type="application/x-www-form-urlencoded"
        )
        assert response.status_code == 302


class TestPeriodoDeleteView:
    def test_deletes_periodo(self, client, user, periodo):
        client.force_login(user)
        url = reverse("periodo_delete", kwargs={"item_id": periodo.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert not Periodo.objects.filter(id=periodo.id).exists()

    def test_returns_204_no_content(self, client, user, periodo):
        client.force_login(user)
        url = reverse("periodo_delete", kwargs={"item_id": periodo.id})
        response = client.delete(url)
        assert response.status_code == 204
        assert response.content == b""

    def test_sets_hx_trigger_on_delete(self, client, user, periodo):
        client.force_login(user)
        url = reverse("periodo_delete", kwargs={"item_id": periodo.id})
        response = client.delete(url)
        assert response["HX-Trigger"] == "periodo-deleted"
