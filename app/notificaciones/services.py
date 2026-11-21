from .models import Notificacion

MENSAJES_NOTIFICACION = {
    "NUEVO_OFRECIMIENTO": "Han ofrecido ayudarte con tu publicación.",

    "REPARTIDOR_ELEGIDO": "¡Has sido seleccionado para realizar la entrega!",

    "POSTULACION_RECHAZADA": "Tu ofrecimiento no fue seleccionado.",

    "FORO_CERRADO": "La convocatoria de tu publicación ha finalizado. Ya tienes un repartidor asignado.",

    "SOLICITUD_CANCELACION_AUTOR": "El autor ha solicitado cancelar la entrega.",

    "SOLICITUD_CANCELACION_REPARTIDOR": "El repartidor ha solicitado cancelar la entrega.",

    "CANCELACION_APROBADA": "La cancelación de la entrega ha sido aprobada.",

    "CANCELACION_RECHAZADA": "La solicitud de cancelación ha sido rechazada.",

    "ENTREGA_COMPLETADA": "La entrega ha sido completada."
}

def crear_notificacion(destinatario, tipo, evento_id, usuario_origen=None, detalle=None):
    "Crea una notificación para un usuario."

    mensaje = MENSAJES_NOTIFICACION.get(tipo)

    if mensaje is None:
        raise ValueError(f"Tipo de notificación desconocido: {tipo}")
    
    "creada es un bool que indica si tuvo que crear una notificación nueva y notificacion es el objeto Notificacion encontrado o creado"
    notificacion, creada = Notificacion.objects.get_or_create(
        destinatario=destinatario,
        evento_id=evento_id,
        defaults={
            "tipo": tipo,
            "mensaje": f"{detalle}. {mensaje}" if detalle else mensaje,
            "usuario_origen": usuario_origen,
        }
    )
    return notificacion