"""Vistas de la API de postulaciones."""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.db import IntegrityError

from .services import ofrecer_ayuda


@login_required
@require_POST
def crear_postulacion(request, publicacion_id):

    try:
        postulacion = ofrecer_ayuda(publicacion_id, request.user)
    except ValidationError as error:
        return JsonResponse({"error": error.messages[0]}, status=400)
    except IntegrityError:
        return JsonResponse(
            {"error": "Ya existe una postulación vigente"},
            status=409
        )

    return JsonResponse({
        "mensaje": "Postulación enviada",
        "postulacion_id": postulacion.pk
    }, status=201)