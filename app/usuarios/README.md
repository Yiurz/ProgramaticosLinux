# Usuarios

La aplicación gestiona el registro, la sesión y el perfil propio. El modelo de autenticación es `usuarios.Usuario`, una subclase de `AbstractUser`. El registro solicita nombre de usuario, RUT único, celular, contraseña y un tipo de cuenta (`DISCAPACITADO` o `REPARTIDOR`). Para relacionar otros modelos con el usuario, usa `settings.AUTH_USER_MODEL`.

## Rutas

| Ruta | Métodos | Función |
| --- | --- | --- |
| `/registro/` | GET, POST | Crear una cuenta e iniciar sesión |
| `/login/` | GET, POST | Iniciar sesión |
| `/logout/` | POST | Cerrar sesión |
| `/` | GET | Ver el inicio y acceder a «Mi perfil» |
| `/api/v1/usuarios/perfil/` | GET, POST | Consultar el perfil propio y actualizar su foto |

## Foto de perfil

La foto es opcional tanto para cuentas nuevas como existentes. El formulario admite archivos JPG, PNG o WebP de hasta 5 MB y requiere sesión y token CSRF. Solo actualiza la foto del usuario autenticado. Los archivos se guardan en `usuarios/perfiles/` dentro de `MEDIA_ROOT`. En desarrollo, Django los sirve bajo `/media/`.

La migración `0007_usuario_foto_perfil` incorpora el campo a instalaciones existentes. Con las dependencias de `app/requirements.txt` instaladas, ejecuta `python manage.py migrate` desde `app/` para aplicar las migraciones.
