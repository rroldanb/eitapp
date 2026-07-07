import pytest
from django.urls import reverse

from apps.mandantes.models import Contacto, Mandante

pytestmark = pytest.mark.django_db


class TestMandantesListView:
    def test_renders_template(self, client, user):
        client.force_login(user)
        url = reverse("mandantes")
        response = client.get(url)
        assert response.status_code == 200
        assert "mandantes.html" in [t.name for t in response.templates]

    def test_lists_mandantes(self, client, user, mandante):
        client.force_login(user)
        url = reverse("mandantes")
        response = client.get(url)
        assert response.status_code == 200
        assert mandante.name in response.content.decode()

    def test_redirects_anon(self, client):
        url = reverse("mandantes")
        response = client.get(url)
        assert response.status_code == 302

    def test_empty_list(self, client, user):
        client.force_login(user)
        url = reverse("mandantes")
        response = client.get(url)
        assert response.status_code == 200


class TestMandanteCreateView:
    def test_get_renders_form(self, client, user):
        client.force_login(user)
        url = reverse("mandante_create")
        response = client.get(url)
        assert response.status_code == 200
        assert "mandante_create.html" in [t.name for t in response.templates]

    def test_post_creates_mandante(self, client, user):
        client.force_login(user)
        url = reverse("mandante_create")
        response = client.post(url, {"name": "Nuevo", "location": "Loc", "details": ""})
        assert response.status_code == 302
        assert Mandante.objects.filter(name="Nuevo").exists()

    def test_post_rejects_empty_name(self, client, user):
        client.force_login(user)
        url = reverse("mandante_create")
        response = client.post(url, {"name": "", "location": "Loc"})
        assert response.status_code == 200
        assert "mandante_create.html" in [t.name for t in response.templates]

    def test_redirects_anon(self, client):
        url = reverse("mandante_create")
        response = client.get(url)
        assert response.status_code == 302


class TestMandanteDetailView:
    def test_get_renders_detail(self, client, user, mandante):
        client.force_login(user)
        url = reverse("mandante_detail", kwargs={"mandante_id": mandante.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "mandante_detail.html" in [t.name for t in response.templates]
        assert mandante.name in response.content.decode()

    def test_post_updates_mandante(self, client, user, mandante):
        client.force_login(user)
        url = reverse("mandante_detail", kwargs={"mandante_id": mandante.id})
        response = client.post(url, {"name": "Updated", "location": "Loc2", "details": ""})
        assert response.status_code == 302
        mandante.refresh_from_db()
        assert mandante.name == "Updated"

    def test_post_shows_error_on_invalid(self, client, user, mandante):
        client.force_login(user)
        url = reverse("mandante_detail", kwargs={"mandante_id": mandante.id})
        response = client.post(url, {"name": "", "location": "Loc"})
        assert response.status_code == 200
        assert "mandante_detail.html" in [t.name for t in response.templates]

    def test_404_for_invalid_id(self, client, user):
        client.force_login(user)
        url = reverse(
            "mandante_detail", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_redirects_anon(self, client):
        url = reverse(
            "mandante_detail", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 302


class TestMandanteDeleteView:
    def test_deletes_mandante(self, client, user, mandante):
        client.force_login(user)
        url = reverse("mandante_delete", kwargs={"mandante_id": mandante.id})
        response = client.post(url)
        assert response.status_code == 302
        assert not Mandante.objects.filter(id=mandante.id).exists()

    def test_404_for_invalid_id(self, client, user):
        client.force_login(user)
        url = reverse(
            "mandante_delete", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.post(url)
        assert response.status_code == 404

    def test_redirects_anon(self, client):
        url = reverse(
            "mandante_delete", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.post(url)
        assert response.status_code == 302


class TestContactosListView:
    def test_renders_template(self, client, user, mandante):
        client.force_login(user)
        url = reverse("contactos", kwargs={"mandante_id": mandante.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "contactos.html" in [t.name for t in response.templates]

    def test_lists_contactos(self, client, user, mandante):
        client.force_login(user)
        Contacto.objects.create(name="C1", mandante=mandante)
        url = reverse("contactos", kwargs={"mandante_id": mandante.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "C1" in response.content.decode()

    def test_404_for_invalid_mandante(self, client, user):
        client.force_login(user)
        url = reverse("contactos", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"})
        response = client.get(url)
        assert response.status_code == 404

    def test_redirects_anon(self, client):
        url = reverse("contactos", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"})
        response = client.get(url)
        assert response.status_code == 302


class TestContactoDetailView:
    def test_get_renders_detail(self, client, user, mandante):
        client.force_login(user)
        c = Contacto.objects.create(name="C1", mandante=mandante)
        url = reverse("contacto_detail", kwargs={"contacto_id": c.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "contacto_detail.html" in [t.name for t in response.templates]
        assert c.name in response.content.decode()

    def test_post_updates_contacto(self, client, user, mandante):
        client.force_login(user)
        c = Contacto.objects.create(name="C1", mandante=mandante)
        url = reverse("contacto_detail", kwargs={"contacto_id": c.id})
        response = client.post(
            url,
            {
                "name": "Updated",
                "email": "",
                "phone": "",
                "cargo": "",
                "position": "",
                "details": "",
            },
        )
        assert response.status_code == 302
        c.refresh_from_db()
        assert c.name == "Updated"

    def test_404_for_invalid_id(self, client, user):
        client.force_login(user)
        url = reverse(
            "contacto_detail", kwargs={"contacto_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_redirects_anon(self, client):
        url = reverse(
            "contacto_detail", kwargs={"contacto_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 302


class TestContactoDeleteView:
    def test_deletes_contacto(self, client, user, mandante):
        client.force_login(user)
        c = Contacto.objects.create(name="C1", mandante=mandante)
        url = reverse("contacto_delete", kwargs={"contacto_id": c.id})
        response = client.post(url)
        assert response.status_code == 302
        assert not Contacto.objects.filter(id=c.id).exists()

    def test_404_for_invalid_id(self, client, user):
        client.force_login(user)
        url = reverse(
            "contacto_delete", kwargs={"contacto_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.post(url)
        assert response.status_code == 404

    def test_redirects_anon(self, client):
        url = reverse(
            "contacto_delete", kwargs={"contacto_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.post(url)
        assert response.status_code == 302


class TestContactoCreateView:
    def test_get_renders_form(self, client, user, mandante):
        client.force_login(user)
        url = reverse("contacto_create", kwargs={"mandante_id": mandante.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "contacto_create.html" in [t.name for t in response.templates]

    def test_post_creates_contacto(self, client, user, mandante):
        client.force_login(user)
        url = reverse("contacto_create", kwargs={"mandante_id": mandante.id})
        response = client.post(
            url,
            {
                "name": "Nuevo Contacto",
                "email": "",
                "phone": "",
                "cargo": "",
                "position": "",
                "details": "",
            },
        )
        assert response.status_code == 302
        assert Contacto.objects.filter(name="Nuevo Contacto", mandante=mandante).exists()

    def test_post_rejects_empty_name(self, client, user, mandante):
        client.force_login(user)
        url = reverse("contacto_create", kwargs={"mandante_id": mandante.id})
        response = client.post(url, {"name": ""})
        assert response.status_code == 200
        assert "contacto_create.html" in [t.name for t in response.templates]

    def test_404_for_invalid_mandante(self, client, user):
        client.force_login(user)
        url = reverse(
            "contacto_create", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_redirects_anon(self, client):
        url = reverse(
            "contacto_create", kwargs={"mandante_id": "00000000-0000-0000-0000-000000000000"}
        )
        response = client.get(url)
        assert response.status_code == 302
