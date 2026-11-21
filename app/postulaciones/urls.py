from django.urls import path
from . import views

urlpatterns = [
    path(
        "<int:publicacion_id>/postular/",
        views.crear_postulacion,
        name="crear_postulacion"
    ),
]