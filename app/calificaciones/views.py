from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import F

from pedidos.models import Pedido
from .models import Calificaciones


@login_required
@require_POST
def calificar_entrega(request, pedido_id):

    try:
        nueva_calificacion = int(
            request.POST.get('calificacion')
        )
    except (ValueError, TypeError):
        return JsonResponse(
            {'error': 'Calificación inválida'},
            status=400
        )

    if nueva_calificacion not in (0, 1, 2, 3, 4, 5):
        return JsonResponse(
            {'error': 'La calificación debe estar entre 0 y 5'},
            status=400
        )

    with transaction.atomic():

        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            id=pedido_id,
            cliente=request.user,
            estado='activo'
        )

        # Verificar que la entrega fue realizada.
        # Sustituir por el campo real de tu modelo Pedido.
        if not pedido.entregado:
            return JsonResponse(
                {'error': 'La entrega aún no fue realizada'},
                status=400
            )

        if Calificaciones.objects.filter(pedido=pedido).exists():
            return JsonResponse(
                {'error': 'Este pedido ya fue calificado'},
                status=400
            )

        calificacion = Calificaciones.objects.create(
            pedido=pedido,
            nueva_calificacion=nueva_calificacion
        )

        calificacion.procesar_calificacion()

        repartidor = pedido.repartidor

        pedido.estado = 'completado'
        pedido.save(update_fields=['estado'])

    return JsonResponse({
        'mensaje': 'Calificación registrada correctamente',
        'nuevo_promedio': repartidor.calificacion_promedio,
        'puntos': repartidor.puntos
    })