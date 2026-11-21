from django.urls import path
from . import views

urlpatterns = [
    path(
        "<int:pedido_id>/calificar/",
        views.calificar_entrega,
        name="calificar_entrega"
    ),
]