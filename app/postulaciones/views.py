"""Vistas de la API de postulaciones."""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction

from .models import Publicacion, Postulacion


@login_required
@require_POST
def crear_postulacion(request, publicacion_id):

    try:
        with transaction.atomic():
            publicacion = get_object_or_404(
                Publicacion.objects.select_for_update(),
                pk=publicacion_id
            )

            if not publicacion.visible:
                return JsonResponse(
                    {"error": "La publicación no está abierta"},
                    status=400
                )

            if publicacion.autor_id == request.user.pk:
                return JsonResponse(
                    {"error": "No puedes postular a tu publicación"},
                    status=400
                )

            if Postulacion.objects.filter(
                publicacion=publicacion,
                repartidor=request.user,
                estado__in=["pendiente", "en_espera", "aceptada"]
            ).exists():
                return JsonResponse(
                    {"error": "Ya tienes una postulación vigente"},
                    status=400
                )

            postulacion = Postulacion.objects.create(
                publicacion=publicacion,
                repartidor=request.user
            )

    except IntegrityError:
        return JsonResponse(
            {"error": "Ya existe una postulación vigente"},
            status=409
        )

    return JsonResponse({
        "mensaje": "Postulación enviada",
        "postulacion_id": postulacion.pk
    }, status=201)