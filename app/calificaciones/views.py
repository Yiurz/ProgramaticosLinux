from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from pedidos.gestor import GestorPedidos


@login_required
@require_POST
def calificar_entrega(request, pedido_id):

    try:
        nota = int(request.POST.get("calificacion", ""))
    except (TypeError, ValueError):
        return JsonResponse({
            "error": "Calificación inválida"
        }, status=400)

    try:
        calificacion = GestorPedidos.completar_pedido(
            pedido_id,
            request.user,
            nota
        )
    except ValidationError as error:
        return JsonResponse({
            "error": error.messages
        }, status=400)

    repartidor = calificacion.pedido.repartidor

    return JsonResponse({
        "mensaje": "Entrega completada y calificada",
        "promedio": repartidor.calificacion_promedio,
        "puntos": repartidor.puntos
    })