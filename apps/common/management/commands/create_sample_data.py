from datetime import date, time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto
from apps.red_vial.models import (
    Arco,
    Calle,
    CoeficienteCruce,
    ConfiguracionTransyt,
    FaseSemaforica,
    Nodo,
    ParametroArco,
    Periodizacion,
    Periodo,
    PuntoControl,
    Regulacion,
    ResumenFlujo,
)


class Command(BaseCommand):
    help = "Crea un proyecto de demostración con datos de ejemplo"

    def handle(self, *args, **options):
        self._create_user()
        self._create_regulaciones()
        self._create_coeficientes()
        mandante = self._create_mandante()
        proyecto = self._create_proyecto(mandante)
        self._clean_proyecto(proyecto)
        calles = self._create_calles(proyecto)
        nodos = self._create_nodos(proyecto, calles)
        arcos = self._create_arcos(proyecto, nodos)
        periodos = self._create_periodos(proyecto)
        pcs = self._create_puntos_control(proyecto, nodos, arcos, periodos)
        self._create_parametros_arco(proyecto, pcs)
        self._create_fases_semaforicas(proyecto, pcs)
        self._create_configuracion_transyt(proyecto)
        self._create_periodizacion(proyecto, pcs, periodos)
        self._create_resumen_flujo(proyecto, pcs, periodos)
        self.stdout.write(self.style.SUCCESS("Proyecto demo creado exitosamente"))

    def _clean_proyecto(self, proyecto: Proyecto) -> None:
        """Elimina datos previos del proyecto para regenerarlos limpios."""
        Periodizacion.objects.filter(pc__proyecto=proyecto).delete()
        ResumenFlujo.objects.filter(pc__proyecto=proyecto).delete()
        ParametroArco.objects.filter(proyecto=proyecto).delete()
        FaseSemaforica.objects.filter(proyecto=proyecto).delete()
        ConfiguracionTransyt.objects.filter(proyecto=proyecto).delete()
        PuntoControl.objects.filter(proyecto=proyecto).delete()
        Arco.objects.filter(proyecto=proyecto).delete()
        Calle.objects.filter(proyecto=proyecto).delete()
        Nodo.objects.filter(proyecto=proyecto).delete()
        Periodo.objects.filter(proyecto=proyecto).delete()

    def _create_user(self) -> User:
        user, _ = User.objects.get_or_create(
            username="demo",
            defaults={"is_staff": True},
        )
        user.set_password("demo123")
        user.save()
        return user

    def _create_regulaciones(self) -> None:
        for codigo, descripcion in [
            ("PARE", "Señal de pare / stop"),
            ("CEDA", "Ceda el paso"),
            ("SEM01", "Semáforo con etapa fija"),
            ("LIBRE", "Paso libre sin regulación"),
        ]:
            Regulacion.objects.get_or_create(codigo=codigo, defaults={"descripcion": descripcion})

    def _create_coeficientes(self) -> None:
        for nomenclatura, tipo, coef in [
            ("VL", "Vehículo Liviano", 1.0),
            ("TXC", "Taxi Colectivo", 1.5),
            ("TXB", "Taxi Bus", 2.0),
            ("C2E", "Camión 2 Ejes", 2.5),
            ("C_MAS2E", "Camión +2 Ejes", 3.0),
            ("PEAT", "Peatón", 0.3),
            ("CICL", "Ciclista", 0.2),
            ("MOTO", "Motocicleta", 0.5),
        ]:
            CoeficienteCruce.objects.get_or_create(
                nomenclatura=nomenclatura,
                proyecto=None,
                defaults={"tipo_transporte": tipo, "coeficiente": coef, "is_standard": True},
            )

    def _create_mandante(self) -> Mandante:
        mandante, _ = Mandante.objects.get_or_create(
            name="Municipalidad de Santiago",
            defaults={"location": "Santiago Centro", "details": "Comuna piloto"},
        )
        return mandante

    def _create_proyecto(self, mandante: Mandante) -> Proyecto:
        user = User.objects.get(username="demo")
        proyecto, _ = Proyecto.objects.get_or_create(
            title="Estudio de Semáforos Av. Libertador",
            defaults={
                "description": "Actualización de planes de tiempo y análisis de flujos",
                "mandante": mandante,
                "user": user,
                "date_started": timezone.make_aware(timezone.datetime(2025, 3, 1)),
            },
        )
        return proyecto

    def _create_calles(self, proyecto: Proyecto) -> dict[str, Calle]:
        calles = {}
        for numero, nombre in [
            (1, "Av. Libertador"),
            (2, "Av. Providencia"),
            (3, "Av. Manuel Montt"),
            (4, "Av. Alameda"),
        ]:
            calle, _ = Calle.objects.get_or_create(
                numero=numero, proyecto=proyecto, defaults={"nombre": nombre}
            )
            calles[nombre] = calle
        return calles

    def _create_nodos(self, proyecto: Proyecto, calles: dict[str, Calle]) -> dict[int, Nodo]:
        nodos = {}
        data = [
            (1, "Av. Libertador con Av. Providencia", "Av. Libertador", "Av. Providencia", 1),
            (2, "Av. Libertador con Av. Manuel Montt", "Av. Libertador", "Av. Manuel Montt", 2),
            (3, "Av. Libertador con Alameda", "Av. Libertador", "Av. Alameda", 3),
        ]
        for numero, interseccion, c1, c2, pc_num in data:
            nodo, _ = Nodo.objects.get_or_create(
                numero=numero,
                proyecto=proyecto,
                defaults={
                    "interseccion": interseccion,
                    "calle_1": calles[c1],
                    "calle_2": calles[c2],
                    "numero_pc": pc_num,
                },
            )
            nodos[numero] = nodo
        return nodos

    def _create_arcos(self, proyecto: Proyecto, nodos: dict[int, Nodo]) -> dict[str, Arco]:
        arcos = {}
        data = [
            (1, 2, 150.0),
            (2, 1, 150.0),
            (1, 3, 200.0),
            (3, 1, 200.0),
            (2, 3, 180.0),
            (3, 2, 180.0),
        ]
        for origen, destino, longitud in data:
            arco, _ = Arco.objects.get_or_create(
                nodo_origen=nodos[origen],
                nodo_destino=nodos[destino],
                proyecto=proyecto,
                defaults={"longitud": longitud},
            )
            key = f"{origen}>{destino}"
            arcos[key] = arco
        return arcos

    def _create_periodos(self, proyecto: Proyecto) -> dict[str, Periodo]:
        periodos = {}
        data = [
            ("PM-L", time(6, 0), time(9, 0), True),
            ("PT-L", time(18, 0), time(21, 0), True),
        ]
        for codigo, inicio, fin, laboral in data:
            periodo, _ = Periodo.objects.get_or_create(
                codigo=codigo,
                proyecto=proyecto,
                defaults={"hora_inicio": inicio, "hora_fin": fin, "es_laboral": laboral},
            )
            periodos[codigo] = periodo
        return periodos

    def _create_puntos_control(
        self,
        proyecto: Proyecto,
        nodos: dict[int, Nodo],
        arcos: dict[str, Arco],
        periodos: dict[str, Periodo],
    ) -> dict[str, PuntoControl]:
        regulacion = Regulacion.objects.get(codigo="SEM01")
        pcs = {}
        # (pc_key, nodo, movimiento, viraje, prioritario, arco_entrada, arco_salida, pistas)
        data = [
            ("pc1_n1_12", nodos[1], "12", "DIR", True, "1>2", "2>1", 2.0),
            ("pc2_n1_13", nodos[1], "13", "IZQ", False, "1>3", "3>1", 1.0),
            ("pc3_n2_21", nodos[2], "21", "DIR", True, "2>1", "1>2", 2.0),
            ("pc4_n2_23", nodos[2], "23", "DER", False, "2>3", "3>2", 1.0),
            ("pc5_n3_31", nodos[3], "31", "DIR", True, "3>1", "1>3", 2.0),
        ]
        for key, nodo, movimiento, viraje, prioritario, arco_in, arco_out, pistas in data:
            pc, _ = PuntoControl.objects.get_or_create(
                nodo=nodo,
                movimiento=movimiento,
                proyecto=proyecto,
                defaults={
                    "viraje": viraje,
                    "is_prioritario": prioritario,
                    "arco_entrada": arcos[arco_in],
                    "arco_salida": arcos[arco_out],
                    "regulacion": regulacion,
                    "numero_pistas": pistas,
                },
            )
            pcs[key] = pc
        return pcs

    def _create_parametros_arco(self, proyecto: Proyecto, pcs: dict[str, PuntoControl]) -> None:
        data = [
            (pcs["pc1_n1_12"], 1800.0, 1.0, 1.0, 10.0, True),
            (pcs["pc2_n1_13"], 1400.0, 1.2, 0.9, None, False),
            (pcs["pc3_n2_21"], 1600.0, 1.2, 0.8, None, False),
            (pcs["pc4_n2_23"], 1500.0, 1.0, 1.0, 8.0, True),
            (pcs["pc5_n3_31"], 1700.0, 1.1, 0.9, None, False),
        ]
        for pc, flujo_sat, pond_dem, pond_det, cap_cola, tiene_t38 in data:
            ParametroArco.objects.get_or_create(
                punto_control=pc,
                proyecto=proyecto,
                defaults={
                    "flujo_saturacion": flujo_sat,
                    "ponderador_demora": pond_dem,
                    "ponderador_detencion": pond_det,
                    "capacidad_cola": cap_cola,
                    "tiene_tarjeta_38": tiene_t38,
                },
            )

    def _create_fases_semaforicas(self, proyecto: Proyecto, pcs: dict[str, PuntoControl]) -> None:
        data = [
            (pcs["pc1_n1_12"], 1, 0.0, 25.0),
            (pcs["pc1_n1_12"], 2, 30.0, 55.0),
            (pcs["pc2_n1_13"], 1, 5.0, 20.0),
            (pcs["pc2_n1_13"], 2, 30.0, 50.0),
            (pcs["pc3_n2_21"], 1, 0.0, 20.0),
            (pcs["pc3_n2_21"], 2, 25.0, 45.0),
            (pcs["pc4_n2_23"], 1, 0.0, 15.0),
            (pcs["pc4_n2_23"], 2, 25.0, 40.0),
            (pcs["pc5_n3_31"], 1, 0.0, 22.0),
            (pcs["pc5_n3_31"], 2, 28.0, 50.0),
        ]
        for pc, fase, inicio, fin in data:
            FaseSemaforica.objects.get_or_create(
                punto_control=pc,
                fase_numero=fase,
                proyecto=proyecto,
                defaults={"verde_inicio": inicio, "verde_fin": fin},
            )

    def _create_configuracion_transyt(self, proyecto: Proyecto) -> None:
        ConfiguracionTransyt.objects.get_or_create(
            proyecto=proyecto,
            defaults={
                "ciclo": 60,
                "W": 10.0,
                "K": 0.5,
                "perdida_inicial": 2.0,
                "ganancia_final": 1.0,
            },
        )

    def _create_periodizacion(
        self, proyecto: Proyecto, pcs: dict[str, PuntoControl], periodos: dict[str, Periodo]
    ) -> None:
        import random

        fecha = date(2025, 3, 17)
        for pc in pcs.values():
            pc_mov = f"{pc.arco_salida.codigo_arco}_{pc.arco_entrada.codigo_arco}"
            for periodo in periodos.values():
                h_start = periodo.hora_inicio.hour
                h_end = periodo.hora_fin.hour
                for hour in range(h_start, h_end):
                    for minute in (0, 15, 30, 45):
                        base = 500 if "PM" in periodo.codigo else 300
                        Periodizacion.objects.get_or_create(
                            fecha=fecha,
                            pc_mov=pc_mov,
                            hora=time(hour, minute),
                            pc=pc,
                            periodo=periodo,
                            defaults={
                                "vl": random.randint(base - 100, base + 200),
                                "txc": random.randint(30, 80),
                                "txb": random.randint(10, 30),
                                "c2e": random.randint(8, 25),
                                "c_mas2e": random.randint(2, 10),
                                "peat": random.randint(50, 200),
                                "cicl": random.randint(10, 40),
                                "moto": random.randint(15, 50),
                            },
                        )

    def _create_resumen_flujo(
        self, proyecto: Proyecto, pcs: dict[str, PuntoControl], periodos: dict[str, Periodo]
    ) -> None:
        for pc in pcs.values():
            for periodo in periodos.values():
                conteos = Periodizacion.objects.filter(pc=pc, periodo=periodo)
                if conteos.exists():
                    total = sum(c.ftot for c in conteos)
                    n = conteos.count()
                    ResumenFlujo.objects.get_or_create(
                        pc=pc,
                        periodo=periodo,
                        defaults={
                            "flujo": int(total / max(n, 1) * 4) if n else None,
                            "flujo_total": total,
                            "promedio": total / max(n, 1),
                            "num_registros": n,
                        },
                    )
