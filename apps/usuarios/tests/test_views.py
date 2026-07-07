import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.usuarios.models import Role

pytestmark = pytest.mark.django_db


class TestHomeView:
    def test_renders_for_anon(self, client):
        url = reverse("home")
        response = client.get(url)
        assert response.status_code == 200
        assert "home.html" in [t.name for t in response.templates]

    def test_renders_for_authenticated(self, client, user):
        client.force_login(user)
        url = reverse("home")
        response = client.get(url)
        assert response.status_code == 200
        assert "home.html" in [t.name for t in response.templates]


class TestSigninView:
    def test_get_renders_form(self, client):
        url = reverse("signin")
        response = client.get(url)
        assert response.status_code == 200
        assert "signin.html" in [t.name for t in response.templates]

    def test_post_logs_in_valid_user(self, client, user):
        user.set_password("12345")
        user.save()
        url = reverse("signin")
        response = client.post(url, {"username": "testuser", "password": "12345"})
        assert response.status_code == 302

    def test_post_rejects_invalid_password(self, client, user):
        url = reverse("signin")
        response = client.post(url, {"username": "testuser", "password": "wrong"})
        assert response.status_code == 200
        assert "signin.html" in [t.name for t in response.templates]

    def test_post_rejects_nonexistent_user(self, client):
        url = reverse("signin")
        response = client.post(url, {"username": "nobody", "password": "x"})
        assert response.status_code == 200

    def test_post_respects_next_param(self, client, user):
        user.set_password("12345")
        user.save()
        url = reverse("signin") + "?next=/mandantes/"
        response = client.post(url, {"username": "testuser", "password": "12345"})
        assert response.status_code == 302
        assert response.url == "/mandantes/"


class TestSignoutView:
    def test_logs_out(self, client, user):
        client.force_login(user)
        url = reverse("signout")
        response = client.get(url)
        assert response.status_code == 302

    def test_redirects_anon(self, client):
        url = reverse("signout")
        response = client.get(url)
        assert response.status_code == 302


class TestHealthcheckView:
    def test_returns_json(self, client):
        url = reverse("health")
        response = client.get(url)
        assert response.status_code in (200, 503)
        data = json.loads(response.content)
        assert "_overall" in data
        assert "_active_db" in data

    def test_reports_default_db(self, client):
        url = reverse("health")
        response = client.get(url)
        data = json.loads(response.content)
        assert "default" in data


class TestSwitchDbView:
    def test_sets_session_and_redirects(self, client):
        url = reverse("switch_db", kwargs={"alias": "pg_local"})
        response = client.get(url, HTTP_REFERER="/mandantes/")
        assert response.status_code == 302
        assert client.session.get("active_db") == "pg_local"

    def test_redirects_to_home_without_referer(self, client):
        url = reverse("switch_db", kwargs={"alias": "default"})
        response = client.get(url)
        assert response.status_code == 302


class TestUserManagementView:
    def test_renders_for_staff(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        client.force_login(staff)
        url = reverse("user_management")
        response = client.get(url)
        assert response.status_code == 200
        assert "user_management.html" in [t.name for t in response.templates]
        assert "staff" in response.content.decode()

    def test_returns_partial_for_htmx(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        client.force_login(staff)
        url = reverse("user_management")
        response = client.get(url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "_user_table.html" in [t.name for t in response.templates]

    def test_redirects_non_staff(self, client, user):
        client.force_login(user)
        url = reverse("user_management")
        response = client.get(url)
        assert response.status_code == 302

    def test_redirects_anon(self, client):
        url = reverse("user_management")
        response = client.get(url)
        assert response.status_code == 302

    def test_supports_sort_params(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        client.force_login(staff)
        url = reverse("user_management") + "?sort_by=username&sort_order=asc"
        response = client.get(url)
        assert response.status_code == 200


class TestAdminCreateUserView:
    def test_post_creates_user(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        client.force_login(staff)
        url = reverse("admin_create_user")
        response = client.post(
            url,
            {
                "username": "newuser",
                "password1": "pAss123!",
                "password2": "pAss123!",
                "role": Role.MODELADOR,
            },
        )
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()
        new_user = User.objects.get(username="newuser")
        assert new_user.profile.role == Role.MODELADOR

    def test_redirects_non_staff(self, client, user):
        client.force_login(user)
        url = reverse("admin_create_user")
        response = client.post(url, {"username": "x"})
        assert response.status_code == 302

    def test_redirects_anon(self, client):
        url = reverse("admin_create_user")
        response = client.post(url, {"username": "x"})
        assert response.status_code == 302


class TestUserToggleActiveView:
    def test_toggles_active(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        target = User.objects.create_user(username="target", password="x")
        client.force_login(staff)
        url = reverse("user_toggle_active", kwargs={"user_id": target.id})
        response = client.post(url)
        assert response.status_code == 302
        target.refresh_from_db()
        assert target.is_active is False

    def test_does_not_disable_self(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        client.force_login(staff)
        url = reverse("user_toggle_active", kwargs={"user_id": staff.id})
        response = client.post(url)
        assert response.status_code == 302
        staff.refresh_from_db()
        assert staff.is_active is True

    def test_redirects_non_staff(self, client, user):
        client.force_login(user)
        url = reverse("user_toggle_active", kwargs={"user_id": user.id})
        response = client.post(url)
        assert response.status_code == 302


class TestUserChangeRoleView:
    def test_changes_role(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        target = User.objects.create_user(username="target", password="x")
        client.force_login(staff)
        url = reverse("user_change_role", kwargs={"user_id": target.id})
        response = client.post(url, {"role": Role.ADMIN})
        assert response.status_code == 302
        target.refresh_from_db()
        assert target.profile.role == Role.ADMIN

    def test_does_not_change_own_role(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        client.force_login(staff)
        url = reverse("user_change_role", kwargs={"user_id": staff.id})
        response = client.post(url, {"role": Role.ADMIN})
        assert response.status_code == 302
        staff.refresh_from_db()
        assert staff.profile.role == Role.ENCUESTADOR

    def test_redirects_non_staff(self, client, user):
        client.force_login(user)
        url = reverse("user_change_role", kwargs={"user_id": user.id})
        response = client.post(url, {"role": Role.ADMIN})
        assert response.status_code == 302


class TestUserChangePasswordView:
    def test_get_renders_form(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        target = User.objects.create_user(username="target", password="oldpass")
        client.force_login(staff)
        url = reverse("user_change_password", kwargs={"user_id": target.id})
        response = client.get(url)
        assert response.status_code == 200
        assert "user_change_password.html" in [t.name for t in response.templates]

    def test_post_changes_password(self, client):
        staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        target = User.objects.create_user(username="target", password="oldpass")
        client.force_login(staff)
        url = reverse("user_change_password", kwargs={"user_id": target.id})
        response = client.post(
            url, {"new_password1": "NuevoPass123!", "new_password2": "NuevoPass123!"}
        )
        assert response.status_code == 302
        target.refresh_from_db()
        assert target.check_password("NuevoPass123!")

    def test_redirects_non_staff(self, client, user):
        target = User.objects.create_user(username="target", password="x")
        client.force_login(user)
        url = reverse("user_change_password", kwargs={"user_id": target.id})
        response = client.get(url)
        assert response.status_code == 302

    def test_redirects_anon(self, client):
        url = reverse("user_change_password", kwargs={"user_id": 1})
        response = client.get(url)
        assert response.status_code == 302
