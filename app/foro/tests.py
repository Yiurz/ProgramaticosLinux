from django.test import TestCase
from django.urls import reverse

from pedidos.models import Pedido
from postulaciones.models import Publicacion, Postulacion
from usuarios.models import Usuario


class ForoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for nombre, rol in (("autora", Usuario.Tipos.DISCAPACITADO),
                            ("otra", Usuario.Tipos.DISCAPACITADO),
                            ("ana", Usuario.Tipos.REPARTIDOR),
                            ("juan", Usuario.Tipos.REPARTIDOR)):
            setattr(cls, nombre, Usuario.objects.create_user(username=nombre, tipo_usuario=rol, rut_id=nombre))

    def publicar(self, usuario, titulo):
        self.client.force_login(usuario)
        return self.client.post(reverse("foro:publicar"), {"titulo": titulo, "descripcion": "Retiro en el casino"})

    def test_roles_y_privacidad(self):
        self.assertEqual(self.client.get(reverse("tablon")).status_code, 302)
        self.assertEqual(self.publicar(self.ana, "Ajena").status_code, 403)
        self.publicar(self.autora, "Mi almuerzo")
        self.publicar(self.autora, "Segundo")
        self.assertEqual(Publicacion.objects.count(), 1)
        pub = Publicacion.objects.get()
        self.client.force_login(self.otra)
        self.assertNotContains(self.client.get(reverse("tablon")), pub.titulo)
        for ruta in ("foro:ofrecer", "crear_postulacion"):
            self.assertEqual(self.client.post(reverse(ruta, args=[pub.pk])).status_code, 403)

    def test_ofertas_entrega_y_nueva_publicacion(self):
        self.publicar(self.autora, "Colación")
        pub = Publicacion.objects.get()
        self.publicar(self.otra, "Jugo")
        otra_pub = Publicacion.objects.get(autor=self.otra)
        for usuario in (self.ana, self.juan):
            self.client.force_login(usuario)
            self.assertContains(self.client.get(reverse("tablon")), "Colación")
            self.client.post(reverse("foro:ofrecer", args=[pub.pk]))
            self.assertContains(self.client.get(reverse("tablon")), "Esperando aprobación")
        oferta = Postulacion.objects.get(repartidor=self.ana)
        self.client.force_login(self.otra)
        self.assertEqual(self.client.post(reverse("foro:elegir", args=[oferta.pk])).status_code, 404)
        self.client.force_login(self.autora)
        pagina = self.client.get(reverse("tablon"))
        for texto in ("ana", "juan", "Sin puntaje", "Entregas completadas: 0"):
            self.assertContains(pagina, texto)
        self.assertEqual(self.autora.notificaciones.filter(tipo="NUEVO_OFRECIMIENTO").count(), 2)
        self.client.post(reverse("foro:elegir", args=[oferta.pk]))
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.repartidor, self.ana)
        self.assertTrue(self.juan.postulaciones_enviadas.filter(estado=Postulacion.Estado.DESCARTADA).exists())
        self.assertTrue(self.juan.notificaciones.filter(tipo="POSTULACION_RECHAZADA").exists())
        self.assertTrue(self.ana.notificaciones.filter(tipo="REPARTIDOR_ELEGIDO").exists())
        entrega = reverse("foro:entregar", args=[pedido.pk])
        self.assertEqual(self.client.post(entrega).status_code, 403)
        self.client.force_login(self.juan)
        self.assertEqual(self.client.post(entrega).status_code, 404)
        self.client.force_login(self.ana)
        self.client.post(reverse("foro:ofrecer", args=[otra_pub.pk]))
        self.assertFalse(otra_pub.postulaciones.exists())
        self.client.post(entrega)
        self.client.post(entrega)
        self.ana.refresh_from_db()
        self.assertEqual(self.ana.entregas_totales, 1)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.COMPLETADO)
        self.assertNotIn(pub, self.client.get(reverse("tablon")).context["publicaciones"])
        self.client.post(reverse("foro:ofrecer", args=[otra_pub.pk]))
        self.assertTrue(otra_pub.postulaciones.filter(repartidor=self.ana).exists())
        self.publicar(self.autora, "Otro almuerzo")
        pagina = self.client.get(reverse("tablon"))
        self.assertContains(pagina, "Otro almuerzo")
        self.assertNotContains(pagina, "Jugo")
        self.client.post(reverse("foro:leer"))
        self.assertFalse(self.autora.notificaciones.filter(leida=False).exists())
        self.assertTrue(self.ana.notificaciones.filter(leida=False).exists())
