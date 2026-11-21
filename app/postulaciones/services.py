from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from notificaciones.services import crear_notificacion
from pedidos.models import Pedido
from usuarios.models import Usuario
from .models import Postulacion, Publicacion


@transaction.atomic
def ofrecer_ayuda(publicacion_id, usuario):
    if usuario.tipo_usuario != Usuario.Tipos.REPARTIDOR:
        raise PermissionDenied
    publicacion = get_object_or_404(Publicacion.objects.select_for_update(), pk=publicacion_id)
    if not publicacion.visible or publicacion.autor_id == usuario.pk:
        raise ValidationError("Esta publicación no admite ofrecimientos.")
    if Pedido.objects.filter(repartidor=usuario, estado=Pedido.Estado.ACTIVO).exists():
        raise ValidationError("Termina tu entrega actual antes de ofrecer ayuda.")
    if publicacion.postulaciones.filter(
        repartidor=usuario, estado__in=Postulacion.ESTADOS_VIGENTES
    ).exists():
        raise ValidationError("Ya enviaste un ofrecimiento para esta publicación.")
    oferta = Postulacion.objects.create(publicacion=publicacion, repartidor=usuario)
    crear_notificacion(publicacion.autor, "NUEVO_OFRECIMIENTO", f"oferta-{oferta.pk}",
                       usuario, detalle=f"{usuario.username} · {publicacion.titulo}")
    return oferta
