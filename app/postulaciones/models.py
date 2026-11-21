"""Modelos de postulaciones."""
from django.conf import settings
from django.db import models
from django.db.models import Q


class Publicacion(models.Model):

    class Estado(models.TextChoices):
        ABIERTA = "abierta", "Abierta"
        ASIGNADA = "asignada", "Asignada"
        EN_ESPERA = "en_espera", "En espera"
        ELIMINADA = "eliminada", "Eliminada"

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="publicaciones"
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTA
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def visible(self):
        return self.estado == self.Estado.ABIERTA


class Postulacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_ESPERA = "en_espera", "En espera"
        ACEPTADA = "aceptada", "Aceptada"
        DESCARTADA = "descartada", "Descartada"
        CANCELADA = "cancelada", "Cancelada"

    publicacion = models.ForeignKey(
        Publicacion,
        on_delete=models.CASCADE,
        related_name="postulaciones"
    )

    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="postulaciones_enviadas"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publicacion", "repartidor"],
                condition=Q(
                    estado__in=[
                        "pendiente", "en_espera", "aceptada"
                    ]
                ),
                name="postulacion_unica_vigente"
            )
        ]