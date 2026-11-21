from django.urls import path
from . import views

urlpatterns = [
    path(
        'calificar/<int:pedido_id>/',
        views.calificar_entrega,
        name='calificar_entrega'
    ),
]