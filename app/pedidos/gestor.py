from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from notificaciones.services import crear_notificacion
from postulaciones.models import Publicacion, Postulacion
from .models import Pedido, SolicitudCancelacion


class GestorPedidos:

    @staticmethod
    @transaction.atomic
    def iniciar_pedido(postulacion_id, cliente):

        if cliente.tipo_usuario != cliente.Tipos.DISCAPACITADO:
            raise PermissionDenied
        postulacion = Postulacion.objects.get(
            pk=postulacion_id
        )

        publicacion = Publicacion.objects.select_for_update().get(
            pk=postulacion.publicacion_id
        )

        if publicacion.autor_id != cliente.pk:
            raise ValidationError(
                "Solo el autor puede aceptar postulaciones"
            )

        if publicacion.estado not in (
            Publicacion.Estado.ABIERTA,
            Publicacion.Estado.EN_ESPERA
        ):
            raise ValidationError(
                "La publicación no admite nuevas asignaciones"
            )

        postulacion = Postulacion.objects.select_for_update().get(
            pk=postulacion_id
        )

        if postulacion.estado not in (
            Postulacion.Estado.PENDIENTE,
            Postulacion.Estado.EN_ESPERA
        ):
            raise ValidationError(
                "La postulación no está disponible"
            )

        if postulacion.repartidor.tipo_usuario != cliente.Tipos.REPARTIDOR:
            raise ValidationError("Esta cuenta no puede realizar entregas")
        if cliente.pk == postulacion.repartidor_id:
            raise ValidationError(
                "No puedes entregar tu propio pedido"
            )

        # Bloquear ambos usuarios en orden estable
        Usuario = get_user_model()
        ids = sorted([cliente.pk, postulacion.repartidor_id])

        list(
            Usuario.objects.select_for_update()
            .filter(pk__in=ids)
            .order_by("pk")
        )

        # Comprobar participación en cualquier rol
        from django.db.models import Q

        ocupados = Pedido.objects.filter(
            estado=Pedido.Estado.ACTIVO
        ).filter(
            Q(cliente_id__in=ids) |
            Q(repartidor_id__in=ids)
        ).exists()

        if ocupados:
            raise ValidationError(
                "Uno de los usuarios ya tiene un pedido activo"
            )

        pedido = Pedido.objects.create(
            publicacion=publicacion,
            postulacion=postulacion,
            cliente=cliente,
            repartidor_id=postulacion.repartidor_id
        )

        postulacion.estado = Postulacion.Estado.ACEPTADA
        postulacion.save(update_fields=["estado"])

        restantes = Postulacion.objects.select_related("repartidor").filter(
            publicacion=publicacion,
            estado__in=[
                Postulacion.Estado.PENDIENTE,
                Postulacion.Estado.EN_ESPERA
            ]
        ).exclude(pk=postulacion.pk)
        for otra in restantes:
            crear_notificacion(otra.repartidor, "POSTULACION_RECHAZADA", f"descartada-{otra.pk}",
                               cliente, detalle=publicacion.titulo)
        restantes.update(estado=Postulacion.Estado.DESCARTADA)
        crear_notificacion(postulacion.repartidor, "REPARTIDOR_ELEGIDO", f"aceptada-{postulacion.pk}",
                           cliente, detalle=publicacion.titulo)

        publicacion.estado = Publicacion.Estado.ASIGNADA
        publicacion.save(update_fields=["estado"])

        return pedido

    @staticmethod
    @transaction.atomic
    def solicitar_cancelacion(
        pedido_id, usuario, motivo, reportar=False
    ):

        pedido = Pedido.objects.select_for_update().get(
            pk=pedido_id
        )

        if usuario.pk not in (
            pedido.cliente_id,
            pedido.repartidor_id
        ):
            raise ValidationError(
                "No participas en este pedido"
            )

        if pedido.estado != Pedido.Estado.ACTIVO:
            raise ValidationError(
                "El pedido no está activo"
            )

        motivo = motivo.strip()

        if not motivo:
            raise ValidationError(
                "Debes indicar el motivo"
            )

        if SolicitudCancelacion.objects.filter(
            pedido=pedido,
            estado=SolicitudCancelacion.Estado.PENDIENTE
        ).exists():
            raise ValidationError(
                "Ya existe una cancelación pendiente"
            )

        # Identificar al otro participante
        if usuario.pk == pedido.cliente_id:
            otro_usuario_id = pedido.repartidor_id
        else:
            otro_usuario_id = pedido.cliente_id

        solicitud = SolicitudCancelacion.objects.create(
            pedido=pedido,
            solicitante=usuario,
            motivo=motivo,
            reportar=reportar,
            reportado_id=otro_usuario_id if reportar else None,
            estado=(
                SolicitudCancelacion.Estado.APROBADA
                if reportar
                else SolicitudCancelacion.Estado.PENDIENTE
            ),
            fecha_decision=timezone.now() if reportar else None
        )

        if reportar:
            GestorPedidos._cancelar_pedido(pedido)

        return solicitud

    @staticmethod
    @transaction.atomic
    def decidir_cancelacion(solicitud_id, usuario, aprobar):

        solicitud_inicial = SolicitudCancelacion.objects.get(
            pk=solicitud_id
        )

        pedido = Pedido.objects.select_for_update().get(
            pk=solicitud_inicial.pedido_id
        )

        solicitud = SolicitudCancelacion.objects.select_for_update().get(
            pk=solicitud_id
        )

        if pedido.estado != Pedido.Estado.ACTIVO:
            raise ValidationError("El pedido ya terminó")

        if solicitud.estado != SolicitudCancelacion.Estado.PENDIENTE:
            raise ValidationError(
                "La solicitud ya fue respondida"
            )

        if solicitud.reportar:
            raise ValidationError(
                "Los reportes no requieren aprobación"
            )

        participantes = {
            pedido.cliente_id,
            pedido.repartidor_id
        }

        if usuario.pk not in participantes:
            raise ValidationError(
                "No participas en este pedido"
            )

        if usuario.pk == solicitud.solicitante_id:
            raise ValidationError(
                "No puedes aprobar tu propia solicitud"
            )

        solicitud.fecha_decision = timezone.now()

        if aprobar:
            solicitud.estado = SolicitudCancelacion.Estado.APROBADA
            GestorPedidos._cancelar_pedido(pedido)
        else:
            solicitud.estado = SolicitudCancelacion.Estado.RECHAZADA

        solicitud.save(update_fields=[
            "estado",
            "fecha_decision"
        ])

        return solicitud

    @staticmethod
    @transaction.atomic
    def completar_pedido(pedido_id, cliente, nota):

        from calificaciones.models import Calificaciones
        from django.db.models import Q

        if type(nota) is not int or nota not in range(6):
            raise ValidationError(
                "La calificación debe estar entre 0 y 5"
            )

        pedido = Pedido.objects.select_for_update().get(
            pk=pedido_id
        )

        if pedido.cliente_id != cliente.pk:
            raise ValidationError(
                "Solo el cliente puede calificar"
            )

        if pedido.estado != Pedido.Estado.ACTIVO:
            raise ValidationError(
                "El pedido no está activo"
            )

        if not pedido.entrega_confirmada:
            raise ValidationError(
                "La entrega todavía no fue confirmada"
            )

        if SolicitudCancelacion.objects.filter(
            pedido=pedido,
            estado=SolicitudCancelacion.Estado.PENDIENTE
        ).exists():
            raise ValidationError(
                "Hay una cancelación pendiente"
            )

        # Bloquear al repartidor antes de actualizar acumulados
        Usuario = get_user_model()
        repartidor = Usuario.objects.select_for_update().get(
            pk=pedido.repartidor_id
        )

        pedido.repartidor = repartidor

        calificacion = Calificaciones.objects.create(
            pedido=pedido,
            nueva_calificacion=nota
        )

        calificacion.procesar_calificacion()

        pedido.estado = Pedido.Estado.COMPLETADO
        pedido.fecha_fin = timezone.now()
        pedido.save(update_fields=["estado", "fecha_fin"])

        # Eliminar lógicamente la publicación
        publicacion = pedido.publicacion
        publicacion.estado = Publicacion.Estado.ELIMINADA
        publicacion.save(update_fields=["estado"])

        # Descartar las solicitudes restantes
        Postulacion.objects.filter(
            publicacion=publicacion,
            estado__in=[
                Postulacion.Estado.PENDIENTE,
                Postulacion.Estado.EN_ESPERA
            ]
        ).update(estado=Postulacion.Estado.DESCARTADA)

        return calificacion

    @staticmethod
    def _cancelar_pedido(pedido):

        pedido.estado = Pedido.Estado.CANCELADO
        pedido.fecha_fin = timezone.now()
        pedido.save(update_fields=["estado", "fecha_fin"])

        pedido.postulacion.estado = Postulacion.Estado.CANCELADA
        pedido.postulacion.save(update_fields=["estado"])

        publicacion = pedido.publicacion
        publicacion.estado = Publicacion.Estado.EN_ESPERA
        publicacion.save(update_fields=["estado"])