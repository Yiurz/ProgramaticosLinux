from django.conf import settings
from django.db import models
from django.db.models import Q, F


class Pedido(models.Model):

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        CANCELADO = "cancelado", "Cancelado"
        COMPLETADO = "completado", "Completado"

    publicacion = models.ForeignKey(
        "postulaciones.Publicacion",
        on_delete=models.PROTECT,
        related_name="pedidos"
    )

    postulacion = models.OneToOneField(
        "postulaciones.Postulacion",
        on_delete=models.PROTECT,
        related_name="pedido"
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos_como_cliente"
    )

    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pedidos_como_repartidor"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO
    )

    entrega_confirmada = models.BooleanField(default=False)

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
                condition=~Q(cliente=F("repartidor")),
                name="cliente_distinto_repartidor"
            ),
        ]

class SolicitudCancelacion(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        APROBADA = "aprobada", "Aprobada"
        RECHAZADA = "rechazada", "Rechazada"

    pedido = models.ForeignKey(
        "pedidos.Pedido",
        on_delete=models.PROTECT,
        related_name="cancelaciones"
    )

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="cancelaciones_solicitadas"
    )

    motivo = models.TextField()

    reportar = models.BooleanField(default=False)

    reportado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reportes_recibidos"
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )

    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_decision = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["pedido"],
                condition=Q(estado="pendiente"),
                name="una_cancelacion_pendiente_por_pedido"
            )
        ]