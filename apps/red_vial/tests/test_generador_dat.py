from pathlib import Path
from django.test import TestCase

from apps.red_vial.services.generador_dat import DatGenerator


REFERENCE_DAT = Path(__file__).parent.parent.parent.parent / 'context' / 'Red_PM..dat'


class ValidateOutputTest(TestCase):
    def setUp(self):
        with open(REFERENCE_DAT, 'rb') as f:
            self.reference_raw = f.read()
        self.reference_text = self.reference_raw.decode('ascii')

    def test_reference_file_passes_validation(self):
        """El archivo de referencia debe pasar validate_output sin errores."""
        gen = DatGenerator(proyecto=None)
        errors = gen.validate_output(self.reference_text)
        self.assertEqual([], errors, f'El archivo de referencia tiene errores: {errors}')

    def test_all_lines_80_chars(self):
        """Todas las líneas del archivo de referencia deben tener 80 caracteres."""
        lines = self.reference_text.split('\r\n')
        lines = [l for l in lines if l]
        for i, line in enumerate(lines):
            self.assertEqual(
                80, len(line),
                f'Línea {i+1} tiene {len(line)} caracteres (se esperan 80): "{line}"'
            )

    def test_ends_with_crlf(self):
        """El archivo debe terminar con CRLF."""
        self.assertTrue(self.reference_raw.endswith(b'\r\n'), 'El archivo no termina con CRLF')

    def test_cards_32_percentages_in_range(self):
        """Los porcentajes de viraje en Card 32 deben estar en 0-1000 (décimas de %)."""
        lines = self.reference_text.splitlines()

        for i, line in enumerate(lines):
            if not line.startswith('   32'):
                continue
            fields = [line[j:j+5].strip() for j in range(0, len(line), 5)]
            for j in range(5, len(fields), 3):
                pct_str = fields[j] if j < len(fields) else ''
                phase_str = fields[j+1] if j+1 < len(fields) else ''
                if pct_str and pct_str.isdigit():
                    pct = int(pct_str)
                    self.assertLessEqual(
                        pct, 1500,
                        f'Card 32 línea {i+1}, campo {j+1}: porcentaje {pct} fuera de rango (> 150.0%)'
                    )

    def test_invalid_content_catches_bad_line_length(self):
        """Contenido con línea muy larga debe reportar error."""
        gen = DatGenerator(proyecto=None)
        bad = 'A' * 90
        errors = gen.validate_output(bad + '\r\n')
        self.assertTrue(any('90' in e for e in errors))

    def test_invalid_content_catches_no_crlf(self):
        """Contenido sin CRLF debe reportar error."""
        gen = DatGenerator(proyecto=None)
        content = '   1    0'.ljust(80)
        errors = gen.validate_output(content)
        self.assertTrue(any('CRLF' in e for e in errors),
                        f'Se esperaba error de CRLF, se obtuvo: {errors}')

    def test_empty_content_reports_error(self):
        """Contenido vacío debe reportar error."""
        gen = DatGenerator(proyecto=None)
        errors = gen.validate_output('')
        self.assertTrue(len(errors) > 0)
