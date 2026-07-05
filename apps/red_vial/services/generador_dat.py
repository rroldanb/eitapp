from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.proyectos.models import Proyecto
from apps.red_vial.models import (
    ConfiguracionTransyt,
    FaseSemaforica,
    Nodo,
    ParametroArco,
    Periodo,
    PuntoControl,
    ResumenFlujo,
)


class DatGenerator:
    CARD_WIDTH: int = 80

    def __init__(self, proyecto: Proyecto, periodo_id: str | None = None) -> None:
        self.proyecto = proyecto
        self.periodo_id = periodo_id
        self.errors: list[str] = []

    def i5(self, value: int, field_index: int = 0) -> str:
        return f"{value:>5d}"

    def pad_line(self, fields: list[str]) -> str:
        line = "".join(fields)
        return line.ljust(self.CARD_WIDTH)

    def header_line(self) -> str:
        title = (self.proyecto.title or "SIN TITULO")[:60]
        nodos_pc = Nodo.objects.filter(proyecto=self.proyecto, numero_pc__isnull=False).count()
        return f"  {title:<56}{nodos_pc:>4d}".ljust(self.CARD_WIDTH)

    def card_1(self, config: ConfiguracionTransyt) -> str:
        nint = config.ciclo * 2
        fields = [
            self.i5(1),
            self.i5(nint),
            self.i5(config.ciclo),
            self.i5(config.ciclo),
            self.i5(3),
            self.i5(2),
        ]
        for _ in range(4):
            fields.append(self.i5(0))
        fields.append(self.i5(1))
        for _ in range(3):
            fields.append(self.i5(0))
        fields.append(self.i5(int(config.W * 100)))
        fields.append(self.i5(int(config.K * 100)))
        return self.pad_line(fields)

    def card_2(self) -> str:
        nodos_pc = Nodo.objects.filter(proyecto=self.proyecto, numero_pc__isnull=False).count()
        return self.pad_line([self.i5(2), self.i5(nodos_pc)])

    def cards_11(self):
        lines = []
        nodos_pc = Nodo.objects.filter(proyecto=self.proyecto, numero_pc__isnull=False).order_by(
            "numero_pc"
        )
        for nodo in nodos_pc:
            lines.append(self.pad_line([self.i5(11), self.i5(nodo.numero), self.i5(0)]))
        return lines

    def cards_31(self, periodo):
        lines = []
        pcs = PuntoControl.objects.filter(proyecto=self.proyecto)
        processed_arcos = set()

        for pc in pcs:
            arco = pc.arco_entrada
            codigo = int(arco.codigo_arco)
            if codigo in processed_arcos:
                continue
            processed_arcos.add(codigo)

            flujo = 0
            if periodo:
                rf = ResumenFlujo.objects.filter(pc=pc, periodo=periodo).first()
                if rf and rf.flujo:
                    flujo = rf.flujo

            param = ParametroArco.objects.filter(punto_control=pc).first()
            saturacion = int(param.flujo_saturacion) if param else 1800

            fields = [self.i5(31), self.i5(codigo)]
            for _ in range(8):
                fields.append(self.i5(0))
            fields.append(self.i5(0))
            fields.append(self.i5(flujo))
            fields.append(self.i5(0))
            fields.append(self.i5(saturacion))
            fields.append(self.i5(0))
            fields.append(self.i5(30))
            lines.append(self.pad_line(fields))

        return lines

    def cards_32(self, periodo):
        lines = []
        pcs = PuntoControl.objects.filter(proyecto=self.proyecto)
        entrada_groups = {}
        for pc in pcs:
            key = pc.arco_entrada.id
            if key not in entrada_groups:
                entrada_groups[key] = []
            entrada_groups[key].append(pc)

        for _entrada_id, pc_group in entrada_groups.items():
            entrada = pc_group[0].arco_entrada
            codigo_entrada = int(entrada.codigo_arco)

            flows = {}
            for pc in pc_group:
                flujo = 0
                if periodo:
                    rf = ResumenFlujo.objects.filter(pc=pc, periodo=periodo).first()
                    if rf and rf.flujo:
                        flujo = rf.flujo
                flows[pc.id] = flujo

            total_flow = sum(flows.values()) or 1

            turn_fields = []
            for pc in pc_group:
                codigo_salida = int(pc.arco_salida.codigo_arco)
                pct = round(flows.get(pc.id, 0) / total_flow * 1000)

                fase = FaseSemaforica.objects.filter(
                    proyecto=self.proyecto, punto_control=pc
                ).first()
                fase_num = fase.fase_numero if fase else 1

                turn_fields.extend([codigo_salida, pct, fase_num])

            offset = 0
            if pc_group:
                fase = FaseSemaforica.objects.filter(
                    proyecto=self.proyecto, punto_control=pc_group[0]
                ).first()
                if fase:
                    offset = round(fase.verde_inicio * 10)

            all_fields = [32, codigo_entrada, offset, 0, *turn_fields]
            i5_fields = [self.i5(v) for v in all_fields]
            lines.append(self.pad_line(i5_fields))

        return lines

    def validate(self):
        errors = []
        if not ConfiguracionTransyt.objects.filter(proyecto=self.proyecto).exists():
            errors.append(
                "Configuración TRANSYT: debe configurar los parámetros globales (ciclo, W, K, etc.)"
            )
        pcs = PuntoControl.objects.filter(proyecto=self.proyecto)
        if not pcs.exists():
            errors.append("Puntos de Control: debe definir al menos un punto de control")
        else:
            for pc in pcs:
                if not ParametroArco.objects.filter(punto_control=pc).exists():
                    errors.append(
                        f"Parámetros de Arco: falta definir parámetros para {pc.nombre} ({pc.codigo_pc})"
                    )
                if not FaseSemaforica.objects.filter(
                    proyecto=self.proyecto, punto_control=pc
                ).exists():
                    errors.append(
                        f"Fases Semafóricas: falta definir fases para {pc.nombre} ({pc.codigo_pc})"
                    )
        periodos = Periodo.objects.filter(proyecto=self.proyecto)
        if not periodos.exists():
            errors.append("Períodos: debe definir al menos un período de análisis")
        if not ResumenFlujo.objects.filter(pc__proyecto=self.proyecto).exists():
            errors.append("Resumen de Flujos: debe calcular los flujos para al menos un período")
        return errors

    def generate(self) -> tuple[str | None, list[str]]:
        errors = self.validate()
        if errors:
            return None, errors

        config = get_object_or_404(ConfiguracionTransyt, proyecto=self.proyecto)

        periodo = None
        if self.periodo_id:
            periodo = Periodo.objects.filter(id=self.periodo_id, proyecto=self.proyecto).first()
        if not periodo:
            periodo = Periodo.objects.filter(proyecto=self.proyecto).first()

        lines = []
        lines.append(self.header_line())
        lines.append(self.card_1(config))
        lines.append(self.card_2())
        lines.extend(self.cards_11())
        lines.extend(self.cards_31(periodo))
        lines.extend(self.cards_32(periodo))

        content = "\r\n".join(lines) + "\r\n"
        return content, []

    def generate_all_periods(self) -> dict[str, str]:
        """Genera un .dat por período y devuelve dict {periodo_nombre: contenido}."""
        config = get_object_or_404(ConfiguracionTransyt, proyecto=self.proyecto)
        periodos = Periodo.objects.filter(proyecto=self.proyecto)

        files = {}
        for periodo in periodos:
            lines = []
            lines.append(self.header_line())
            lines.append(self.card_1(config))
            lines.append(self.card_2())
            lines.extend(self.cards_11())
            lines.extend(self.cards_31(periodo))
            lines.extend(self.cards_32(periodo))
            files[periodo.codigo] = "\r\n".join(lines) + "\r\n"
        return files

    def validate_output(self, content):
        """Valida que el contenido generado cumpla con el formato TRANSYT 8S.
        Retorna lista de errores (vacía si todo ok).
        """
        errors = []
        if not content:
            return ["El contenido está vacío"]

        # Normalize line endings: handle both \r\n and \n
        if "\r\n" in content:
            lines = content.split("\r\n")
            has_crlf = True
        else:
            lines = content.split("\n")
            has_crlf = False
        # Remove trailing empty line from final terminator
        if lines and lines[-1] == "":
            lines = lines[:-1]

        if not lines:
            return ["No hay líneas en el contenido"]

        for i, line in enumerate(lines):
            line_num = i + 1

            if len(line) != self.CARD_WIDTH:
                errors.append(
                    f"Línea {line_num}: tiene {len(line)} caracteres (se esperan {self.CARD_WIDTH})"
                )

            if len(line) < 5:
                errors.append(f"Línea {line_num}: muy corta para tener un número de tarjeta")
                continue

            try:
                card_num = int(line[:5].strip())
            except ValueError:
                card_num = line[:5].strip()

            # Skip field validation for header line (non-numeric first line)
            if isinstance(card_num, str) and i == 0:
                continue
            # Validar que cada campo I5 sea numérico o espacio
            for j in range(0, len(line), 5):
                field = line[j : j + 5]
                stripped = field.strip()
                if stripped and not stripped.lstrip("-").isdigit():
                    errors.append(
                        f'Línea {line_num}, campo {j // 5 + 1}: "{field}" no es un entero I5 válido'
                    )

        if not has_crlf:
            errors.append("El archivo no tiene terminación CRLF")

        # Check card ordering (skip header line)
        card_order = []
        for line_ in lines:
            try:
                c = int(line_[:5].strip())
                card_order.append(c)
            except ValueError:
                pass  # header line

        expected_prefix = [1, 2]
        for i, c in enumerate(card_order):
            if i < len(expected_prefix) and c != expected_prefix[i]:
                errors.append(
                    f"Línea {i + 1}: se esperaba tarjeta {expected_prefix[i]}, se encontró {c}"
                )
                break

        return errors


@transaction.atomic
def generar_parametros_arco(proyecto):
    """Crea ParametroArco con defaults para cada PuntoControl que no tenga uno."""
    pcs = PuntoControl.objects.filter(proyecto=proyecto)
    count = 0
    for pc in pcs:
        _, created = ParametroArco.objects.get_or_create(
            proyecto=proyecto,
            punto_control=pc,
            defaults={
                "flujo_saturacion": 1800.0,
                "ponderador_demora": 1.0,
                "ponderador_detencion": 1.0,
            },
        )
        if created:
            count += 1
    return count


@transaction.atomic
def generar_fases_semaforicas(proyecto):
    """Crea FaseSemaforica con defaults para cada PuntoControl que no tenga una."""
    pcs = PuntoControl.objects.filter(proyecto=proyecto)
    count = 0
    for pc in pcs:
        _, created = FaseSemaforica.objects.get_or_create(
            proyecto=proyecto,
            punto_control=pc,
            fase_numero=1,
            defaults={
                "verde_inicio": 0,
                "verde_fin": 30,
            },
        )
        if created:
            count += 1
    return count
