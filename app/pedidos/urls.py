from django.urls import path
from . import views

urlpatterns = [
    path(
        "aceptar/<int:postulacion_id>/",
        views.aceptar_postulacion,
        name="aceptar_postulacion"
    ),
    path(
        "<int:pedido_id>/cancelar/",
        views.solicitar_cancelacion,
        name="solicitar_cancelacion"
    ),
    path(
        "cancelaciones/<int:solicitud_id>/decision/",
        views.decidir_cancelacion,
        name="decidir_cancelacion"
    ),
]