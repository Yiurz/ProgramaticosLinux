"Vistas de la API de notificaciones."

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notificacion
from .serializers import NotificacionSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_notificaciones(request):

    notificaciones = Notificacion.objects.filter(
        destinatario=request.user
    )

    serializer = NotificacionSerializer(
        notificaciones,
        many=True
    )

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def marcar_leida(request, id):

    notificacion = Notificacion.objects.filter(
        id=id,
        destinatario=request.user
    ).first()

    if notificacion is None:
        return Response(
            {"error": "Notificación no encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )

    if notificacion.leida is False:
        notificacion.leida = True
        notificacion.save(update_fields=["leida"])

    return Response(
        {"mensaje": "Notificación marcada como leída."},
        status=status.HTTP_200_OK
    )
