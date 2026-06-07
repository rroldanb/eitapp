from datetime import date, time
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User
from apps.mandantes.models import Mandante, Contacto
from apps.proyectos.models import Proyecto, Imagenes_proyecto
from apps.red_vial.models import (
    Calle, Nodo, Arco, Regulacion, Periodo, PuntoControl,
    Periodizacion, ResumenFlujo, CoeficienteCruce,
    ParametroArco, FaseSemaforica, ConfiguracionTransyt,
)


class ProyectoDeleteCascadeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.mandante = Mandante.objects.create(name="MandanteTest", location="Loc")
        self.contacto = Contacto.objects.create(
            name="ContactoTest", mandante=self.mandante,
            email="c@test.cl", phone="", cargo="", position="", details="",
        )
        self.proyecto = Proyecto.objects.create(
            title="ProyectoTest", user=self.user, mandante=self.mandante,
        )
        # Calle
        self.calle = Calle.objects.create(nombre="Calle A", numero=1, proyecto=self.proyecto)
        # Nodo
        self.nodo1 = Nodo.objects.create(numero=1, interseccion="N1", proyecto=self.proyecto, numero_pc=1)
        self.nodo2 = Nodo.objects.create(numero=2, interseccion="N2", proyecto=self.proyecto, numero_pc=2)
        # Arco
        self.arco1 = Arco.objects.create(nodo_origen=self.nodo1, nodo_destino=self.nodo2, longitud=100.0, proyecto=self.proyecto)
        self.arco2 = Arco.objects.create(nodo_origen=self.nodo2, nodo_destino=self.nodo1, longitud=100.0, proyecto=self.proyecto)
        # Regulacion
        self.regulacion = Regulacion.objects.create(codigo="SEM01", descripcion="Test")
        # Periodo
        self.periodo = Periodo.objects.create(codigo="PM-L", hora_inicio=time(6, 0), hora_fin=time(9, 0), es_laboral=True, proyecto=self.proyecto)
        # PuntoControl
        self.pc = PuntoControl.objects.create(
            nodo=self.nodo1, movimiento="12", viraje="DIR", is_prioritario=True,
            arco_entrada=self.arco1, arco_salida=self.arco2,
            regulacion=self.regulacion, numero_pistas=2, proyecto=self.proyecto,
        )
        # Periodizacion
        self.periodizacion = Periodizacion.objects.create(
            fecha=date(2025, 3, 15), hora=time(6, 0), pc=self.pc, periodo=self.periodo,
            vl=100, txc=20, txb=10, c2e=5, c_mas2e=2, peat=50, cicl=10, moto=5,
        )
        # ResumenFlujo
        self.resumen = ResumenFlujo.objects.create(pc=self.pc, periodo=self.periodo, flujo=100)
        # Imagenes_proyecto
        self.imagen = Imagenes_proyecto.objects.create(image_url="http://example.com/img.jpg", proyecto=self.proyecto)
        # CoeficienteCruce
        self.coef = CoeficienteCruce.objects.create(nomenclatura="VL", tipo_transporte="Vehículo", coeficiente=1.0, is_standard=False, proyecto=self.proyecto)
        # ConfiguracionTransyt
        self.config = ConfiguracionTransyt.objects.create(proyecto=self.proyecto, ciclo=60, W=10.0, K=0.5, perdida_inicial=2.0, ganancia_final=1.0)
        # ParametroArco
        self.param = ParametroArco.objects.create(proyecto=self.proyecto, punto_control=self.pc, flujo_saturacion=1800.0, ponderador_demora=1.0, ponderador_detencion=1.0, capacidad_cola=10.0, tiene_tarjeta_38=True)
        # FaseSemaforica
        self.fase = FaseSemaforica.objects.create(proyecto=self.proyecto, punto_control=self.pc, fase_numero=1, verde_inicio=0.0, verde_fin=25.0)

    def test_cascade_deletes_all_associated_data(self):
        p_id = self.proyecto.id
        # Verify all objects exist before deletion
        self.assertTrue(Proyecto.objects.filter(id=p_id).exists())
        self.assertTrue(Calle.objects.filter(id=self.calle.id).exists())
        self.assertTrue(Nodo.objects.filter(id=self.nodo1.id).exists())
        self.assertTrue(Arco.objects.filter(id=self.arco1.id).exists())
        self.assertTrue(Periodo.objects.filter(id=self.periodo.id).exists())
        self.assertTrue(PuntoControl.objects.filter(id=self.pc.id).exists())
        self.assertTrue(Periodizacion.objects.filter(id=self.periodizacion.id).exists())
        self.assertTrue(ResumenFlujo.objects.filter(id=self.resumen.id).exists())
        self.assertTrue(Imagenes_proyecto.objects.filter(id=self.imagen.id).exists())
        self.assertTrue(CoeficienteCruce.objects.filter(id=self.coef.id).exists())
        self.assertTrue(ConfiguracionTransyt.objects.filter(id=self.config.id).exists())
        self.assertTrue(ParametroArco.objects.filter(id=self.param.id).exists())
        self.assertTrue(FaseSemaforica.objects.filter(id=self.fase.id).exists())

        # Delete proyecto
        self.proyecto.delete()

        # Verify all associated data is cascade-deleted
        self.assertFalse(Proyecto.objects.filter(id=p_id).exists())
        self.assertFalse(Calle.objects.filter(id=self.calle.id).exists())
        self.assertFalse(Nodo.objects.filter(id=self.nodo1.id).exists())
        self.assertFalse(Arco.objects.filter(id=self.arco1.id).exists())
        self.assertFalse(Periodo.objects.filter(id=self.periodo.id).exists())
        self.assertFalse(PuntoControl.objects.filter(id=self.pc.id).exists())
        self.assertFalse(Periodizacion.objects.filter(id=self.periodizacion.id).exists())
        self.assertFalse(ResumenFlujo.objects.filter(id=self.resumen.id).exists())
        self.assertFalse(Imagenes_proyecto.objects.filter(id=self.imagen.id).exists())
        self.assertFalse(CoeficienteCruce.objects.filter(id=self.coef.id).exists())
        self.assertFalse(ConfiguracionTransyt.objects.filter(id=self.config.id).exists())
        self.assertFalse(ParametroArco.objects.filter(id=self.param.id).exists())
        self.assertFalse(FaseSemaforica.objects.filter(id=self.fase.id).exists())

    def test_mandante_and_contacto_survive_project_deletion(self):
        mandante_id = self.mandante.id
        contacto_id = self.contacto.id
        self.proyecto.delete()
        self.assertTrue(Mandante.objects.filter(id=mandante_id).exists())
        self.assertTrue(Contacto.objects.filter(id=contacto_id).exists())

    def test_cascade_does_not_affect_regulacion(self):
        reg_id = self.regulacion.id
        self.proyecto.delete()
        self.assertTrue(Regulacion.objects.filter(id=reg_id).exists())


class ProyectoImageCleanupOnDeleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testimg", password="12345")
        self.mandante = Mandante.objects.create(name="Img Mandante", location="Loc")

    @patch("apps.imagenes.services.storage_service.delete_project_image")
    def test_proyecto_delete_cleans_up_image_url(self, mock_delete):
        proyecto = Proyecto.objects.create(
            title="Img Proyecto", user=self.user, mandante=self.mandante,
            image_url="https://bucket.supabase.co/project-img.webp",
        )
        proyecto.delete()
        mock_delete.assert_called_once_with("https://bucket.supabase.co/project-img.webp")

    @patch("apps.imagenes.services.storage_service.delete_project_image")
    def test_proyecto_delete_without_image(self, mock_delete):
        proyecto = Proyecto.objects.create(
            title="No Img", user=self.user, mandante=self.mandante,
        )
        proyecto.delete()
        mock_delete.assert_not_called()

    @patch("apps.imagenes.services.storage_service.delete_project_image")
    def test_proyecto_cascade_cleans_up_nodo_images(self, mock_delete):
        from apps.red_vial.models import Nodo
        proyecto = Proyecto.objects.create(
            title="Cascade Img", user=self.user, mandante=self.mandante,
            image_url="https://bucket.supabase.co/p-img.webp",
        )
        nodo1 = Nodo.objects.create(
            numero=1, proyecto=proyecto,
            imagen="https://bucket.supabase.co/n1-img.webp",
            plano="https://bucket.supabase.co/n1-plano.webp",
        )
        nodo2 = Nodo.objects.create(
            numero=2, proyecto=proyecto,
            imagen="https://bucket.supabase.co/n2-img.webp",
        )
        proyecto.delete()
        # nodo1.imagen, nodo1.plano, nodo2.imagen + proyecto.image_url
        self.assertEqual(mock_delete.call_count, 4)
        mock_delete.assert_any_call("https://bucket.supabase.co/n1-img.webp")
        mock_delete.assert_any_call("https://bucket.supabase.co/n1-plano.webp")
        mock_delete.assert_any_call("https://bucket.supabase.co/n2-img.webp")
        mock_delete.assert_any_call("https://bucket.supabase.co/p-img.webp")
