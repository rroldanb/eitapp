import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Nodo


class NodoImagenViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.mandante = Mandante.objects.create(name="Test Mandante")
        self.proyecto = Proyecto.objects.create(
            title="Test Proyecto",
            user=self.user,
            mandante=self.mandante,
        )
        self.nodo = Nodo.objects.create(numero=1, proyecto=self.proyecto)
        self.client.force_login(self.user)

    @patch("apps.red_vial.views.nodo_views_cbv.get_image_from_request")
    @patch("apps.red_vial.views.nodo_views_cbv.update_nodo_image")
    def test_upload_image_view_success(self, mock_update, mock_get_image):
        mock_get_image.return_value = SimpleUploadedFile(
            "test.webp", b"data", content_type="image/webp"
        )
        mock_update.return_value = self.nodo

        url = reverse("nodo_upload_image", args=[self.nodo.id])
        response = self.client.post(url, {"image": b"data"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nodo-row")
        mock_get_image.assert_called_once()
        mock_update.assert_called_once()

    @patch("apps.red_vial.views.nodo_views_cbv.get_image_from_request")
    def test_upload_image_view_no_file(self, mock_get_image):
        mock_get_image.return_value = None

        url = reverse("nodo_upload_image", args=[self.nodo.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertIn("No se proporcionó imagen", data["error"])

    def test_upload_image_view_get_method(self):
        url = reverse("nodo_upload_image", args=[self.nodo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_upload_image_view_unauthenticated(self):
        self.client.logout()
        url = reverse("nodo_upload_image", args=[self.nodo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_upload_image_view_nodo_not_found(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        url = reverse("nodo_upload_image", args=[fake_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    @patch("apps.red_vial.views.nodo_views_cbv.delete_nodo_image")
    def test_delete_image_view_success(self, mock_delete):
        mock_delete.return_value = self.nodo

        url = reverse("nodo_delete_image", args=[self.nodo.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nodo-row")
        mock_delete.assert_called_once_with(self.nodo.id)

    def test_delete_image_view_get_method(self):
        url = reverse("nodo_delete_image", args=[self.nodo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_delete_image_view_unauthenticated(self):
        self.client.logout()
        url = reverse("nodo_delete_image", args=[self.nodo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_delete_image_view_nodo_not_found(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        url = reverse("nodo_delete_image", args=[fake_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class NodoImagenServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser2", password="12345")
        self.mandante = Mandante.objects.create(name="Test Mandante 2")
        self.proyecto = Proyecto.objects.create(
            title="Test Proyecto 2",
            user=self.user,
            mandante=self.mandante,
        )
        self.nodo = Nodo.objects.create(
            numero=1,
            proyecto=self.proyecto,
            imagen="https://example.com/old-image.webp",
        )

    @patch("apps.imagenes.services.storage_service.delete_image")
    @patch("apps.imagenes.services.storage_service.upload_image")
    def test_update_nodo_image_with_existing(self, mock_upload, mock_delete):
        from apps.red_vial.services.nodo_service import update_nodo_image

        mock_upload.return_value = "https://example.com/new-image.webp"
        mock_file = MagicMock()

        result = update_nodo_image(self.nodo.id, mock_file)

        self.assertEqual(result.imagen, "https://example.com/new-image.webp")
        mock_delete.assert_called_once_with("https://example.com/old-image.webp")
        mock_upload.assert_called_once_with(mock_file)

    @patch("apps.imagenes.services.storage_service.upload_image")
    def test_update_nodo_image_without_existing(self, mock_upload):
        from apps.red_vial.services.nodo_service import update_nodo_image

        self.nodo.imagen = None
        self.nodo.save()

        mock_upload.return_value = "https://example.com/new-image.webp"
        mock_file = MagicMock()

        result = update_nodo_image(self.nodo.id, mock_file)

        self.assertEqual(result.imagen, "https://example.com/new-image.webp")
        mock_upload.assert_called_once_with(mock_file)

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_image_with_existing(self, mock_delete):
        from apps.red_vial.services.nodo_service import delete_nodo_image

        result = delete_nodo_image(self.nodo.id)

        self.assertIsNone(result.imagen)
        mock_delete.assert_called_once_with("https://example.com/old-image.webp")

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_image_without_existing(self, mock_delete):
        from apps.red_vial.services.nodo_service import delete_nodo_image

        self.nodo.imagen = None
        self.nodo.save()

        result = delete_nodo_image(self.nodo.id)

        self.assertIsNone(result.imagen)
        mock_delete.assert_not_called()


class NodoPlanoViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser3", password="12345")
        self.mandante = Mandante.objects.create(name="Test Mandante 3")
        self.proyecto = Proyecto.objects.create(
            title="Test Proyecto 3",
            user=self.user,
            mandante=self.mandante,
        )
        self.nodo = Nodo.objects.create(numero=2, proyecto=self.proyecto)
        self.client.force_login(self.user)

    @patch("apps.red_vial.views.nodo_views_cbv.get_image_from_request")
    @patch("apps.red_vial.views.nodo_views_cbv.update_nodo_plano")
    def test_upload_plano_view_success(self, mock_update, mock_get_image):
        mock_get_image.return_value = SimpleUploadedFile(
            "test.webp", b"data", content_type="image/webp"
        )
        mock_update.return_value = self.nodo

        url = reverse("nodo_upload_plano", args=[self.nodo.id])
        response = self.client.post(url, {"image": b"data"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nodo-row")
        mock_get_image.assert_called_once()
        mock_update.assert_called_once()

    @patch("apps.red_vial.views.nodo_views_cbv.get_image_from_request")
    def test_upload_plano_view_no_file(self, mock_get_image):
        mock_get_image.return_value = None

        url = reverse("nodo_upload_plano", args=[self.nodo.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data["success"])
        self.assertIn("No se proporcionó imagen", data["error"])

    def test_upload_plano_view_get_method(self):
        url = reverse("nodo_upload_plano", args=[self.nodo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_upload_plano_view_unauthenticated(self):
        self.client.logout()
        url = reverse("nodo_upload_plano", args=[self.nodo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_upload_plano_view_nodo_not_found(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        url = reverse("nodo_upload_plano", args=[fake_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    @patch("apps.red_vial.views.nodo_views_cbv.delete_nodo_plano")
    def test_delete_plano_view_success(self, mock_delete):
        mock_delete.return_value = self.nodo
        url = reverse("nodo_delete_plano", args=[self.nodo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nodo-row")
        mock_delete.assert_called_once_with(self.nodo.id)

    def test_delete_plano_view_get_method(self):
        url = reverse("nodo_delete_plano", args=[self.nodo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_delete_plano_view_nodo_not_found(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        url = reverse("nodo_delete_plano", args=[fake_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class NodoPlanoServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser4", password="12345")
        self.mandante = Mandante.objects.create(name="Test Mandante 4")
        self.proyecto = Proyecto.objects.create(
            title="Test Proyecto 4",
            user=self.user,
            mandante=self.mandante,
        )
        self.nodo = Nodo.objects.create(
            numero=3,
            proyecto=self.proyecto,
            plano="https://example.com/old-plano.webp",
        )

    @patch("apps.imagenes.services.storage_service.delete_image")
    @patch("apps.imagenes.services.storage_service.upload_image")
    def test_update_nodo_plano_with_existing(self, mock_upload, mock_delete):
        from apps.red_vial.services.nodo_service import update_nodo_plano

        mock_upload.return_value = "https://example.com/new-plano.webp"
        mock_file = MagicMock()

        result = update_nodo_plano(self.nodo.id, mock_file)

        self.assertEqual(result.plano, "https://example.com/new-plano.webp")
        mock_delete.assert_called_once_with("https://example.com/old-plano.webp")
        mock_upload.assert_called_once_with(mock_file)

    @patch("apps.imagenes.services.storage_service.upload_image")
    def test_update_nodo_plano_without_existing(self, mock_upload):
        from apps.red_vial.services.nodo_service import update_nodo_plano

        self.nodo.plano = None
        self.nodo.save()

        mock_upload.return_value = "https://example.com/new-plano.webp"
        mock_file = MagicMock()

        result = update_nodo_plano(self.nodo.id, mock_file)

        self.assertEqual(result.plano, "https://example.com/new-plano.webp")
        mock_upload.assert_called_once_with(mock_file)

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_plano_with_existing(self, mock_delete):
        from apps.red_vial.services.nodo_service import delete_nodo_plano

        result = delete_nodo_plano(self.nodo.id)

        self.assertIsNone(result.plano)
        mock_delete.assert_called_once_with("https://example.com/old-plano.webp")

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_plano_without_existing(self, mock_delete):
        from apps.red_vial.services.nodo_service import delete_nodo_plano

        self.nodo.plano = None
        self.nodo.save()

        result = delete_nodo_plano(self.nodo.id)

        self.assertIsNone(result.plano)
        mock_delete.assert_not_called()


class NodoModelDeleteImageCleanupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testdel", password="12345")
        self.mandante = Mandante.objects.create(name="Del Mandante")
        self.proyecto = Proyecto.objects.create(
            title="Del Proyecto",
            user=self.user,
            mandante=self.mandante,
        )

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_cleans_up_both_images(self, mock_delete):
        nodo = Nodo.objects.create(
            numero=1,
            proyecto=self.proyecto,
            imagen="https://bucket.supabase.co/img1.webp",
            plano="https://bucket.supabase.co/plano1.webp",
        )
        nodo.delete()
        self.assertEqual(mock_delete.call_count, 2)
        mock_delete.assert_any_call("https://bucket.supabase.co/img1.webp")
        mock_delete.assert_any_call("https://bucket.supabase.co/plano1.webp")

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_without_images(self, mock_delete):
        nodo = Nodo.objects.create(numero=2, proyecto=self.proyecto)
        nodo.delete()
        mock_delete.assert_not_called()

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_with_only_imagen(self, mock_delete):
        nodo = Nodo.objects.create(
            numero=3,
            proyecto=self.proyecto,
            imagen="https://bucket.supabase.co/img3.webp",
        )
        nodo.delete()
        mock_delete.assert_called_once_with("https://bucket.supabase.co/img3.webp")

    @patch("apps.imagenes.services.storage_service.delete_image")
    def test_delete_nodo_with_only_plano(self, mock_delete):
        nodo = Nodo.objects.create(
            numero=4,
            proyecto=self.proyecto,
            plano="https://bucket.supabase.co/plano4.webp",
        )
        nodo.delete()
        mock_delete.assert_called_once_with("https://bucket.supabase.co/plano4.webp")

    @patch("apps.imagenes.services.storage_service.delete_project_image")
    def test_proyecto_cascade_cleans_up_nodo_images(self, mock_delete):
        Nodo.objects.create(
            numero=10,
            proyecto=self.proyecto,
            imagen="https://bucket.supabase.co/n10-img.webp",
            plano="https://bucket.supabase.co/n10-plano.webp",
        )
        Nodo.objects.create(
            numero=11,
            proyecto=self.proyecto,
            imagen="https://bucket.supabase.co/n11-img.webp",
        )
        self.proyecto.delete()
        # 3 images total: nodo1.imagen, nodo1.plano, nodo2.imagen
        self.assertEqual(mock_delete.call_count, 3)
        mock_delete.assert_any_call("https://bucket.supabase.co/n10-img.webp")
        mock_delete.assert_any_call("https://bucket.supabase.co/n10-plano.webp")
        mock_delete.assert_any_call("https://bucket.supabase.co/n11-img.webp")


class NodoImagesJsonViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser5", password="12345")
        self.mandante = Mandante.objects.create(name="Test Mandante 5")
        self.proyecto = Proyecto.objects.create(
            title="Test Proyecto 5",
            user=self.user,
            mandante=self.mandante,
        )
        self.nodo = Nodo.objects.create(
            numero=10,
            proyecto=self.proyecto,
            imagen="https://example.com/img.webp",
            plano="https://example.com/plano.webp",
        )
        self.client.force_login(self.user)

    def _url(self, nodo_id=None):
        return reverse("nodo_images_json", args=[nodo_id or self.nodo.id])

    def test_returns_both_images(self):
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["imagen"], "https://example.com/img.webp")
        self.assertEqual(data["plano"], "https://example.com/plano.webp")

    def test_returns_empty_when_no_images(self):
        nodo = Nodo.objects.create(numero=11, proyecto=self.proyecto)
        response = self.client.get(self._url(nodo.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["imagen"], "")
        self.assertEqual(data["plano"], "")

    def test_returns_partial_images(self):
        nodo = Nodo.objects.create(
            numero=12, proyecto=self.proyecto, imagen="https://example.com/solo-img.webp"
        )
        response = self.client.get(self._url(nodo.id))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["imagen"], "https://example.com/solo-img.webp")
        self.assertEqual(data["plano"], "")

    def test_404_when_nodo_not_found(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(self._url(fake_id))
        self.assertEqual(response.status_code, 404)

    def test_get_method_only(self):
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 302)
