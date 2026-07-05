import io
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto


class ImportViewsAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.mandante = Mandante.objects.create(name="TM", location="Loc")
        self.proyecto = Proyecto.objects.create(title="TP", user=self.user, mandante=self.mandante)
        self.client.force_login(self.user)

    def _url(self, name, *args):
        return reverse(f"import_{name}", args=args or [self.proyecto.id])

    def _upload_url(self):
        return reverse("import_upload")

    # Helper to create a minimal valid Excel file
    def _make_excel_bytes(self):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Mandante"
        ws.append(["name", "location", "details"])
        ws.append(["TIPO", "", ""])
        ws.append(["DESCRIPCION", "", ""])
        ws.append(["TestMandante", "Loc", "Det"])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        return buf.read()

    # --- Not logged in ---

    def test_import_start_requires_login(self):
        self.client.logout()
        response = self.client.get(self._url("start"))
        self.assertEqual(response.status_code, 302)

    def test_import_upload_requires_login(self):
        self.client.logout()
        response = self.client.post(self._upload_url())
        self.assertEqual(response.status_code, 302)

    def test_import_validate_requires_login(self):
        self.client.logout()
        response = self.client.post(self._url("validate"))
        self.assertEqual(response.status_code, 302)

    def test_import_execute_requires_login(self):
        self.client.logout()
        response = self.client.post(self._url("execute"))
        self.assertEqual(response.status_code, 302)

    def test_import_cancel_requires_login(self):
        self.client.logout()
        response = self.client.post(self._url("cancel"))
        self.assertEqual(response.status_code, 302)

    def test_import_goto_selection_requires_login(self):
        self.client.logout()
        response = self.client.post(self._url("goto_selection"))
        self.assertEqual(response.status_code, 302)

    def test_import_back_step1_requires_login(self):
        self.client.logout()
        response = self.client.post(self._url("back_step1"))
        self.assertEqual(response.status_code, 302)

    # --- import_landing ---

    def test_import_landing_renders(self):
        url = reverse("import_landing")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subir archivo")

    def test_import_landing_requires_login(self):
        self.client.logout()
        url = reverse("import_landing")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    # --- import_start ---

    def test_import_start_clears_session(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": []}
        session["import_filename"] = "test.xlsx"
        session.save()
        response = self.client.get(self._url("start"))
        session = self.client.session
        self.assertNotIn("import_parsed", session)
        self.assertNotIn("import_filename", session)
        self.assertEqual(response.status_code, 200)

    def test_import_start_from_sidebar_sets_flag(self):
        response = self.client.get(self._url("start"), {"from_sidebar": "1"})
        session = self.client.session
        self.assertTrue(session.get("import_from_sidebar"))
        self.assertEqual(response.status_code, 200)

    def test_import_start_renders_template(self):
        response = self.client.get(self._url("start"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subir archivo")

    # --- import_upload ---

    def test_import_upload_success(self):
        excel_content = self._make_excel_bytes()
        file = SimpleUploadedFile(
            "test.xlsx",
            excel_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(self._upload_url(), {"file": file})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn("import_parsed", session)
        self.assertIn("import_filename", session)
        self.assertContains(response, "Configurar")

    def test_import_upload_no_file(self):
        response = self.client.post(self._upload_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debes seleccionar")

    def test_import_upload_wrong_extension(self):
        file = SimpleUploadedFile("test.txt", b"data", content_type="text/plain")
        response = self.client.post(self._upload_url(), {"file": file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solo se aceptan")

    def test_import_upload_parse_error(self):
        file = SimpleUploadedFile(
            "test.xlsx",
            b"not an excel file",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(self._upload_url(), {"file": file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Error al leer")

    def test_import_upload_empty_data(self):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "EmptySheet"
        ws.append(["name"])
        ws.append(["TIPO"])
        ws.append(["DESCRIPCION"])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        file = SimpleUploadedFile(
            "empty.xlsx",
            buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(self._upload_url(), {"file": file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no contiene datos")

    def test_import_upload_clears_old_session(self):
        session = self.client.session
        session["import_validation"] = {"old": "data"}
        session.save()
        excel_content = self._make_excel_bytes()
        file = SimpleUploadedFile(
            "test.xlsx",
            excel_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.client.post(self._upload_url(), {"file": file})
        session = self.client.session
        self.assertNotIn("import_validation", session)

    # --- import_back_step1 ---

    def test_import_back_step1_clears_advanced_keys(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": []}
        session["import_filename"] = "test.xlsx"
        session["import_selected"] = ["Mandante"]
        session["import_validation"] = {"total_valid": 0}
        session["import_report"] = {"Mandante": {}}
        session["import_report_totals"] = {"inserted": 0}
        session.save()
        response = self.client.post(self._url("back_step1"))
        session = self.client.session
        self.assertNotIn("import_selected", session)
        self.assertNotIn("import_validation", session)
        self.assertNotIn("import_report", session)
        self.assertNotIn("import_report_totals", session)
        self.assertEqual(response.status_code, 200)

    # --- import_goto_selection ---

    def test_goto_selection_success(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session.save()
        response = self.client.post(self._url("goto_selection"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecciona las hojas a importar")

    def test_goto_selection_no_parsed(self):
        response = self.client.post(self._url("goto_selection"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sesión expirada")

    def test_goto_selection_with_from_sidebar(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session["import_from_sidebar"] = True
        session.save()
        response = self.client.post(self._url("goto_selection"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecciona las hojas a importar")

    # --- import_validate ---

    def test_import_validate_success(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session.save()
        response = self.client.post(self._url("validate"), {"sheets": ["Mandante"]})
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn("import_selected", session)
        self.assertIn("import_validation", session)
        self.assertContains(response, "Importación completada")
        self.assertContains(response, "1 insertada")

    def test_import_validate_no_parsed(self):
        response = self.client.post(self._url("validate"), {"sheets": ["Mandante"]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sesión expirada")

    def test_import_validate_no_sheets(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session.save()
        response = self.client.post(self._url("validate"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seleccionar al menos una hoja")

    def test_import_validate_empty_sheets_list(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session.save()
        response = self.client.post(self._url("validate"), {"sheets": []})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seleccionar al menos una hoja")

    # --- import_execute ---

    def test_import_execute_success(self):
        validation = {
            "results": {
                "Mandante": {
                    "valid": [{"name": "M1", "location": "L1", "details": ""}],
                    "duplicates": [],
                    "errors": [],
                    "sheet": "Mandante",
                    "total": 1,
                },
            },
            "total_valid": 1,
            "total_errors": 0,
            "total_duplicates": 0,
        }
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session["import_selected"] = ["Mandante"]
        session["import_validation"] = validation
        session.save()
        response = self.client.post(self._url("execute"))
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertIn("import_report", session)
        self.assertIn("import_report_totals", session)
        self.assertContains(response, "Importación completada")
        self.assertTrue(Mandante.objects.filter(name="M1").exists())

    def test_import_execute_no_validation(self):
        response = self.client.post(self._url("execute"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sesión expirada")

    def test_import_execute_with_duplicate_update(self):
        Mandante.objects.create(name="ExistingM", location="OldLoc")
        validation = {
            "results": {
                "Mandante": {
                    "valid": [],
                    "duplicates": [{"name": "ExistingM", "location": "NewLoc", "details": ""}],
                    "errors": [],
                    "sheet": "Mandante",
                    "total": 1,
                },
            },
            "total_valid": 0,
            "total_errors": 0,
            "total_duplicates": 1,
        }
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "ExistingM", "location": "NewLoc"}]}
        session["import_filename"] = "test.xlsx"
        session["import_selected"] = ["Mandante"]
        session["import_validation"] = validation
        session.save()
        response = self.client.post(self._url("execute"), {"dup_Mandante": "update"})
        self.assertEqual(response.status_code, 200)
        mandante = Mandante.objects.get(name="ExistingM")
        self.assertEqual(mandante.location, "NewLoc")

    def test_import_execute_with_duplicate_skip(self):
        Mandante.objects.create(name="ExistingM", location="OldLoc")
        validation = {
            "results": {
                "Mandante": {
                    "valid": [],
                    "duplicates": [{"name": "ExistingM", "location": "NewLoc", "details": ""}],
                    "errors": [],
                    "sheet": "Mandante",
                    "total": 1,
                },
            },
            "total_valid": 0,
            "total_errors": 0,
            "total_duplicates": 1,
        }
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "ExistingM", "location": "NewLoc"}]}
        session["import_filename"] = "test.xlsx"
        session["import_selected"] = ["Mandante"]
        session["import_validation"] = validation
        session.save()
        response = self.client.post(self._url("execute"), {"dup_Mandante": "skip"})
        self.assertEqual(response.status_code, 200)
        mandante = Mandante.objects.get(name="ExistingM")
        self.assertEqual(mandante.location, "OldLoc")

    def test_import_execute_exception(self):
        validation = {
            "results": {
                "Mandante": {
                    "valid": [{"name": "M1", "location": "L1", "details": ""}],
                    "duplicates": [],
                    "errors": [],
                    "sheet": "Mandante",
                    "total": 1,
                },
            },
            "total_valid": 1,
            "total_errors": 0,
            "total_duplicates": 0,
        }
        session = self.client.session
        session["import_parsed"] = {"Mandante": [{"name": "M1", "location": "L1"}]}
        session["import_filename"] = "test.xlsx"
        session["import_selected"] = ["Mandante"]
        session["import_validation"] = validation
        session.save()
        with patch(
            "apps.red_vial.views.import_views.execute_import", side_effect=ValueError("Boom!")
        ):
            response = self.client.post(self._url("execute"))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Error durante la importación")

    # --- import_cancel ---

    def test_import_cancel_clears_session(self):
        session = self.client.session
        session["import_parsed"] = {"Mandante": []}
        session["import_filename"] = "test.xlsx"
        session["import_selected"] = ["Mandante"]
        session.save()
        response = self.client.post(self._url("cancel"))
        session = self.client.session
        for key in list(session.keys()):
            self.assertFalse(key.startswith("import_"), f"Session key '{key}' was not cleared")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Subir archivo")

    # --- GET on POST-only views ---

    def test_upload_get_returns_405(self):
        response = self.client.get(self._upload_url())
        self.assertEqual(response.status_code, 405)

    def test_validate_get_returns_405(self):
        response = self.client.get(self._url("validate"))
        self.assertEqual(response.status_code, 405)

    def test_execute_get_returns_405(self):
        response = self.client.get(self._url("execute"))
        self.assertEqual(response.status_code, 405)

    def test_cancel_get_returns_405(self):
        response = self.client.get(self._url("cancel"))
        self.assertEqual(response.status_code, 405)

    def test_back_step1_get_returns_405(self):
        response = self.client.get(self._url("back_step1"))
        self.assertEqual(response.status_code, 405)

    def test_goto_selection_get_returns_405(self):
        response = self.client.get(self._url("goto_selection"))
        self.assertEqual(response.status_code, 405)
