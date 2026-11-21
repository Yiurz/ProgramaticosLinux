"""Vistas de la API de cancelaciones."""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .gestor import GestorPedidos


def error_validacion(error):
    return JsonResponse({
        "error": error.messages
    }, status=400)


@login_required
@require_POST
def aceptar_postulacion(request, postulacion_id):
    try:
        pedido = GestorPedidos.iniciar_pedido(
            postulacion_id,
            request.user
        )
    except ValidationError as error:
        return error_validacion(error)

    return JsonResponse({
        "mensaje": "Pedido iniciado",
        "pedido_id": pedido.pk
    }, status=201)

@login_required
@require_POST
def decidir_cancelacion(request, solicitud_id):

    decision = request.POST.get("decision")

    if decision not in ("aprobar", "rechazar"):
        return JsonResponse({
            "error": "Decisión inválida"
        }, status=400)

    try:
        solicitud = GestorPedidos.decidir_cancelacion(
            solicitud_id,
            request.user,
            decision == "aprobar"
        )
    except ValidationError as error:
        return error_validacion(error)

    return JsonResponse({
        "mensaje": "Decisión registrada",
        "estado": solicitud.estado
    })

@login_required
@require_POST
def solicitar_cancelacion(request, pedido_id):

    try:
        solicitud = GestorPedidos.solicitar_cancelacion(
            pedido_id=pedido_id,
            usuario=request.user,
            motivo=request.POST.get("motivo", ""),
            reportar=request.POST.get("reportar") == "true"
        )
    except ValidationError as error:
        return JsonResponse({
            "error": error.messages
        }, status=400)

    return JsonResponse({
        "mensaje": (
            "Pedido cancelado por reporte"
            if solicitud.reportar
            else "Solicitud de cancelación enviada"
        ),
        "estado": solicitud.estado,
        "solicitud_id": solicitud.pk
    })