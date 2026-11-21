from django.urls import path

from . import views

app_name = "foro"
urlpatterns = [
    path("bandeja/leer/", views.leer, name="leer"),
    path("publicar/", views.publicar, name="publicar"),
    path("<int:pk>/ofrecer/", views.ofrecer, name="ofrecer"),
    path("postulacion/<int:pk>/elegir/", views.elegir, name="elegir"),
    path("pedido/<int:pk>/entregar/", views.entregar, name="entregar"),
]
