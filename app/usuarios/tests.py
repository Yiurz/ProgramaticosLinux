from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Usuario


def foto(formato="PNG"):
    imagen = BytesIO()
    Image.new("RGB", (2, 2), "blue").save(imagen, formato)
    return SimpleUploadedFile(f"perfil.{formato.lower()}", imagen.getvalue())


class CuentaTests(TestCase):
    def setUp(self):
        self.datos = {
            "username": "ana",
            "rut_id": "12345678-5",
            "celular": "+56912345678",
            "tipo_usuario": Usuario.Tipos.REPARTIDOR,
            "password1": "Ejemplo-de-clave-452!",
            "password2": "Ejemplo-de-clave-452!",
        }

    def test_registro_inicio_y_cierre_de_sesion(self):
        for rol in Usuario.Tipos.values:
            with self.subTest(rol=rol):
                self.assertContains(self.client.get(reverse("registro")), "Crear cuenta")
                datos = {**self.datos, "tipo_usuario": rol, "username": rol.lower()}
                if rol == Usuario.Tipos.DISCAPACITADO:
                    datos["rut_id"] = "11111111-1"
                respuesta = self.client.post(reverse("registro"), datos)
                self.assertRedirects(respuesta, reverse("inicio"))
                usuario = Usuario.objects.get(username=datos["username"])
                self.assertEqual(usuario.tipo_usuario, rol)
                self.assertTrue(usuario.check_password(datos["password1"]))
                self.assertFalse(usuario.foto_perfil)

                self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))
                perfil = reverse("usuarios:perfil")
                self.assertRedirects(self.client.get(perfil), f"{reverse('login')}?next={perfil}")
                respuesta = self.client.post(reverse("login"), {
                    "username": usuario.username, "password": datos["password1"], "next": perfil,
                })
                self.assertRedirects(respuesta, perfil)
                self.client.logout()

    def test_registro_rechaza_datos_invalidos(self):
        Usuario.objects.create_user(username="existente", rut_id="11111111-1", celular="123")
        for campo, valor in (
            ("username", "existente"),
            ("rut_id", "11111111-1"),
            ("tipo_usuario", "ADMIN"),
            ("password2", "otra clave"),
        ):
            with self.subTest(campo=campo):
                respuesta = self.client.post(reverse("registro"), {**self.datos, campo: valor})
                self.assertIn(campo, respuesta.context["form"].errors)
        self.assertEqual(Usuario.objects.count(), 1)


class PerfilTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(username="ana", rut_id="1-9", celular="123")
        cls.otro = Usuario.objects.create_user(username="julio", rut_id="2-7", celular="456")

    def setUp(self):
        media = self.enterContext(TemporaryDirectory())
        self.enterContext(override_settings(MEDIA_ROOT=media))
        self.url = reverse("usuarios:perfil")
        self.client.force_login(self.usuario)

    def test_perfil_requiere_sesion(self):
        self.client.logout()
        for respuesta in (self.client.get(self.url), self.client.post(self.url)):
            self.assertRedirects(respuesta, f"{reverse('login')}?next={self.url}")

    def test_perfil_sin_foto_accesible_desde_inicio(self):
        self.assertContains(self.client.get(reverse("inicio")), self.url)
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, self.usuario.username)
        self.assertContains(respuesta, "Aún no tienes una foto")
        self.assertContains(respuesta, 'enctype="multipart/form-data"')

    def test_subir_y_reemplazar_foto_propia(self):
        anterior = None
        for formato in ("JPEG", "PNG", "WEBP"):
            with self.subTest(formato=formato):
                archivo = foto(formato)
                contenido = archivo.read()
                archivo.seek(0)
                with self.captureOnCommitCallbacks(execute=True):
                    respuesta = self.client.post(self.url, {
                        "foto_perfil": archivo, "usuario": self.otro.pk, "is_staff": True,
                    }, follow=True)
                self.assertRedirects(respuesta, self.url)
                self.usuario.refresh_from_db()
                actual = self.usuario.foto_perfil
                self.assertContains(respuesta, actual.url)
                with actual.open() as guardado:
                    self.assertEqual(guardado.read(), contenido)
                if anterior:
                    self.assertFalse(actual.storage.exists(anterior))
                anterior = actual.name
        self.assertFalse(self.usuario.is_staff)
        self.otro.refresh_from_db()
        self.assertFalse(self.otro.foto_perfil)

    def test_carga_invalida_conserva_la_foto_anterior(self):
        self.client.post(self.url, {"foto_perfil": foto()})
        self.usuario.refresh_from_db()
        anterior = self.usuario.foto_perfil.name
        grande = foto()
        grande.seek(5 * 1024 * 1024)
        grande.write(b"x")
        grande.seek(0)
        for archivo in (None, SimpleUploadedFile("falsa.png", b"texto"), foto("GIF"), grande):
            with self.subTest(archivo=archivo):
                datos = {"foto_perfil": archivo} if archivo else {}
                respuesta = self.client.post(self.url, datos)
                self.assertIn("foto_perfil", respuesta.context["form"].errors)
                self.usuario.refresh_from_db()
                self.assertEqual(self.usuario.foto_perfil.name, anterior)
                self.assertTrue(self.usuario.foto_perfil.storage.exists(anterior))

    def test_subida_requiere_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        self.assertEqual(cliente.post(self.url, {"foto_perfil": foto()}).status_code, 403)
        cliente.get(self.url)
        respuesta = cliente.post(self.url, {
            "foto_perfil": foto(), "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
        })
        self.assertRedirects(respuesta, self.url)
