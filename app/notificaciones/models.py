"Modelos de notificaciones."

from django.db import models
from django.conf import settings

class Notificacion(models.Model):

    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )

    usuario_origen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notificaciones_generadas"
    )

    evento_id = models.CharField(max_length=100)

    tipo = models.CharField(max_length=50)

    mensaje = models.TextField()

    fecha = models.DateTimeField(auto_now_add=True)

    leida = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evento_id", "destinatario"],
                name="unique_notificacion_evento_usuario"
            )
        ]

        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} - {self.destinatario}"
