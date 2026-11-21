"""Modelos de cancelaciones."""
from django.conf import settings
from django.db import models
from django.db.models import Q


class Pedido(models.Model):

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        CANCELADO = "cancelado", "Cancelado"
        COMPLETADO = "completado", "Completado"

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos_cliente"
    )

    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos_repartidor"
    )

    # Ajustar al nombre real de tu aplicación
    publicacion = models.ForeignKey(
        "publicaciones.Publicacion",
        on_delete=models.PROTECT,
        related_name="pedidos"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO
    )

    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cliente"],
                condition=Q(estado="activo"),
                name="cliente_un_pedido_activo"
            ),
            models.UniqueConstraint(
                fields=["repartidor"],
                condition=Q(estado="activo"),
                name="repartidor_un_pedido_activo"
            ),
            models.UniqueConstraint(
                fields=["publicacion"],
                condition=Q(estado="activo"),
                name="publicacion_un_pedido_activo"
            ),
            models.CheckConstraint(
                condition=~Q(cliente=models.F("repartidor")),
                name="pedido_usuarios_distintos"
            ),
        ]

class SolicitudCancelacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="cancelaciones"
    )

    motivo = models.TextField()

    reportar_usuario = models.BooleanField(default=False)

    aprobacion_cliente = models.BooleanField(default=True)
    aprobacion_repartidor = models.BooleanField(null=True)

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_decision = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pedido"],
                condition=Q(estado="pendiente"),
                name="una_cancelacion_pendiente"
            )
        ]