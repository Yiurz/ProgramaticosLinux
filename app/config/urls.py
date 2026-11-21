from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from usuarios import views as usuariosUrl

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/usuarios/', include('usuarios.urls')),
    path('api/v1/foro/', include('foro.urls')),
    path('api/v1/postulaciones/', include('postulaciones.urls')),
    path('api/v1/contacto/', include('contacto.urls')),
    path('api/v1/pedidos/', include('pedidos.urls')),
    path('api/v1/calificaciones/', include('calificaciones.urls')),
    path('api/v1/notificaciones/', include('notificaciones.urls')),

    path("", usuariosUrl.inicio, name="inicio"),
    path("registro/", usuariosUrl.registro, name="registro"),
    path("login/", LoginView.as_view(template_name="usuarios/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
