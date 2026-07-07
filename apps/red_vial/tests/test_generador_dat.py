from pathlib import Path

from django.test import TestCase

from apps.red_vial.models import (
    Arco,
    CoeficienteCruce,
    ConfiguracionTransyt,
    FaseSemaforica,
    Nodo,
    ParametroArco,
    Periodo,
    PuntoControl,
    ResumenFlujo,
)
from apps.red_vial.services.generador_dat import DatGenerator

REFERENCE_DAT = Path(__file__).parent.parent.parent.parent / "context" / "Red_PM..dat"


class ValidateOutputTest(TestCase):
    def setUp(self):
        with open(REFERENCE_DAT, "rb") as f:
            self.reference_raw = f.read()
        self.reference_text = self.reference_raw.decode("ascii")

    def test_reference_file_passes_validation(self):
        """El archivo de referencia debe pasar validate_output sin errores."""
        gen = DatGenerator(proyecto=None)
        errors = gen.validate_output(self.reference_text)
        self.assertEqual([], errors, f"El archivo de referencia tiene errores: {errors}")

    def test_all_lines_80_chars(self):
        """Todas las líneas del archivo de referencia deben tener 80 caracteres."""
        lines = self.reference_text.split("\r\n")
        lines = [line for line in lines if line]
        for i, line in enumerate(lines):
            self.assertEqual(
                80,
                len(line),
                f'Línea {i + 1} tiene {len(line)} caracteres (se esperan 80): "{line}"',
            )

    def test_ends_with_crlf(self):
        """El archivo debe terminar con CRLF."""
        self.assertTrue(self.reference_raw.endswith(b"\r\n"), "El archivo no termina con CRLF")

    def test_cards_32_percentages_in_range(self):
        """Los porcentajes de viraje en Card 32 deben estar en 0-1000 (décimas de %)."""
        lines = self.reference_text.splitlines()

        for i, line in enumerate(lines):
            if not line.startswith("   32"):
                continue
            fields = [line[j : j + 5].strip() for j in range(0, len(line), 5)]
            for j in range(5, len(fields), 3):
                pct_str = fields[j] if j < len(fields) else ""
                fields[j + 1] if j + 1 < len(fields) else ""
                if pct_str and pct_str.isdigit():
                    pct = int(pct_str)
                    self.assertLessEqual(
                        pct,
                        1500,
                        f"Card 32 línea {i + 1}, campo {j + 1}: porcentaje {pct} fuera de rango (> 150.0%)",
                    )

    def test_invalid_content_catches_bad_line_length(self):
        """Contenido con línea muy larga debe reportar error."""
        gen = DatGenerator(proyecto=None)
        bad = "A" * 90
        errors = gen.validate_output(bad + "\r\n")
        self.assertTrue(any("90" in e for e in errors))

    def test_invalid_content_catches_no_crlf(self):
        """Contenido sin CRLF debe reportar error."""
        gen = DatGenerator(proyecto=None)
        content = "   1    0".ljust(80)
        errors = gen.validate_output(content)
        self.assertTrue(
            any("CRLF" in e for e in errors), f"Se esperaba error de CRLF, se obtuvo: {errors}"
        )

    def test_empty_content_reports_error(self):
        """Contenido vacío debe reportar error."""
        gen = DatGenerator(proyecto=None)
        errors = gen.validate_output("")
        self.assertTrue(len(errors) > 0)


class RealGenerationTest(TestCase):
    """Generate a .dat with real model data and validate it."""

    def setUp(self):
        from django.contrib.auth.models import User

        from apps.mandantes.models import Mandante
        from apps.proyectos.models import Proyecto

        self.user = User.objects.create_user(username="testuser", password="12345")
        self.mandante = Mandante.objects.create(name="M", location="L")
        self.proyecto = Proyecto.objects.create(
            title="Proyecto Test DAT",
            user=self.user,
            mandante=self.mandante,
        )
        self.config = ConfiguracionTransyt.objects.create(
            proyecto=self.proyecto,
            ciclo=60,
            W=10.0,
            K=0.5,
            perdida_inicial=2.0,
            ganancia_final=1.0,
        )
        nodo1 = Nodo.objects.create(numero=1, numero_pc=1, proyecto=self.proyecto)
        nodo2 = Nodo.objects.create(numero=2, numero_pc=2, proyecto=self.proyecto)
        arco12 = Arco.objects.create(
            nodo_origen=nodo1, nodo_destino=nodo2, longitud=100, proyecto=self.proyecto
        )
        arco21 = Arco.objects.create(
            nodo_origen=nodo2, nodo_destino=nodo1, longitud=100, proyecto=self.proyecto
        )
        self.periodo = Periodo.objects.create(
            proyecto=self.proyecto,
            codigo="PM-L",
            hora_inicio="07:00",
            hora_fin="09:00",
            es_laboral=True,
        )
        pc1 = PuntoControl.objects.create(
            nodo=nodo1,
            movimiento="12",
            arco_entrada=arco12,
            arco_salida=arco12,
            viraje="DIR",
            is_prioritario=True,
            proyecto=self.proyecto,
        )
        PuntoControl.objects.create(
            nodo=nodo2,
            movimiento="21",
            arco_entrada=arco21,
            arco_salida=arco21,
            viraje="DIR",
            is_prioritario=False,
            proyecto=self.proyecto,
        )
        for pci in [pc1, PuntoControl.objects.get(nodo=nodo2)]:
            ParametroArco.objects.get_or_create(
                proyecto=self.proyecto,
                punto_control=pci,
                defaults={
                    "flujo_saturacion": 1800.0,
                    "ponderador_demora": 1.0,
                    "ponderador_detencion": 1.0,
                },
            )
            FaseSemaforica.objects.get_or_create(
                proyecto=self.proyecto,
                punto_control=pci,
                fase_numero=1,
                defaults={"verde_inicio": 0.0, "verde_fin": 30.0},
            )
        CoeficienteCruce.objects.create(
            nomenclatura="VL",
            tipo_transporte="Vehículo Liviano",
            coeficiente=1.0,
            is_standard=True,
        )
        ResumenFlujo.objects.create(
            pc=pc1,
            periodo=self.periodo,
            flujo=100,
        )

    def test_generate_returns_content_and_no_errors(self):
        gen = DatGenerator(proyecto=self.proyecto, periodo_id=self.periodo.id)
        content, errors = gen.generate()
        self.assertIsNotNone(content)
        self.assertEqual(errors, [])

    def test_generated_content_has_header_line(self):
        gen = DatGenerator(proyecto=self.proyecto, periodo_id=self.periodo.id)
        content, _ = gen.generate()
        self.assertIn("Proyecto Test DAT", content)

    def test_generated_content_starts_with_2_chars(self):
        gen = DatGenerator(proyecto=self.proyecto, periodo_id=self.periodo.id)
        content, _ = gen.generate()
        lines = content.split("\r\n")
        self.assertTrue(lines[0].startswith("  "))

    def test_generated_content_passes_validate_output(self):
        gen = DatGenerator(proyecto=self.proyecto, periodo_id=self.periodo.id)
        content, _ = gen.generate()
        errors = gen.validate_output(content)
        self.assertEqual(errors, [], f"Generated .dat has validation errors: {errors}")

    def test_generate_all_periods_returns_dict(self):
        gen = DatGenerator(proyecto=self.proyecto)
        files = gen.generate_all_periods()
        self.assertIn(self.periodo.codigo, files)
        content = files[self.periodo.codigo]
        self.assertIsNotNone(content)

    def test_generate_without_periodo_uses_first(self):
        gen = DatGenerator(proyecto=self.proyecto)
        content, errors = gen.generate()
        self.assertIsNotNone(content)
        self.assertEqual(errors, [])

    def test_generated_content_ends_with_crlf(self):
        gen = DatGenerator(proyecto=self.proyecto, periodo_id=self.periodo.id)
        content, _ = gen.generate()
        self.assertTrue(content.endswith("\r\n"))

    def test_validate_pre_generation_fails_without_config(self):
        self.config.delete()
        gen = DatGenerator(proyecto=self.proyecto, periodo_id=self.periodo.id)
        content, errors = gen.generate()
        self.assertIsNone(content)
        self.assertTrue(len(errors) > 0)
