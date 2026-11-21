from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/usuarios/', include('usuarios.urls')),
    path('api/v1/foro/', include('foro.urls')),
    path('api/v1/postulaciones/', include('postulaciones.urls')),
    path('api/v1/contacto/', include('contacto.urls')),
    path('api/v1/cancelaciones/', include('cancelaciones.urls')),
    path('api/v1/calificaciones/', include('calificaciones.urls')),
    path('api/v1/notificaciones/', include('notificaciones.urls')),
]
