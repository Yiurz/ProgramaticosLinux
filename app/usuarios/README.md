# Usuarios

Este módulo será la fuente de identidad, rol y datos de contacto para el resto de la API. El registro, el inicio de sesión y la edición del perfil propio vivirán bajo `/api/v1/usuarios/`.

## Crear el modelo antes de migrar

1. En `models.py`, definir `Usuario` como subclase de `django.contrib.auth.models.AbstractUser`. Conservar `username` para iniciar sesión en la primera versión. `email` se ha eliminado, puesto que ya no es obligatorio, junto con `first_name` y `last_name`, solo `username` identificará a un usuario públicamente
2. Agregar `telefono` como `models.CharField(max_length=32)` para conservar el prefijo internacional y los ceros iniciales. Validar y normalizar el formato al editarlo. Definir `TipoUsuario` con `models.TextChoices` y los valores estables `DISCAPACITADO` («Persona con discapacidad») y `REPARTIDOR` («Repartidor»). Declarar `tipo_usuario` como `models.CharField(max_length=20, choices=TipoUsuario.choices)`. Exigir exactamente un rol al registrarse.
3. En `config/settings.py`, establecer `AUTH_USER_MODEL = "usuarios.Usuario"` junto con la creación del modelo. Desde `app/`, ejecutar `python manage.py makemigrations usuarios`, verificar que `0001_initial` crea el usuario y recién entonces ejecutar `python manage.py migrate`. Si una instalación ya tiene usuarios y migraciones aplicadas, planificar la migración de sus datos antes de cambiar el modelo. [Guía de autenticación personalizada de Django](https://docs.djangoproject.com/en/6.1/topics/auth/customizing/)
4. Para incorporar campos posteriores, decidir tipo, obligatoriedad y visibilidad. Si existen filas y el nuevo campo es obligatorio, agregarlo inicialmente como opcional, completar sus valores y aplicar una segunda migración para exigirlo. Actualizar los formularios, la validación de la API y los campos de alta y edición de `UserAdmin` al habilitar el administrador. Incluir los campos obligatorios pertinentes en `REQUIRED_FIELDS` para `createsuperuser`.
5. En otros modelos usar `settings.AUTH_USER_MODEL` en las relaciones. Para obtener la clase en vistas o servicios, usar `get_user_model()`.

## Registro, sesión y permisos

Proponer `POST registro/`, `POST sesion/`, `POST cerrar-sesion/` y `GET/PATCH yo/` como rutas relativas. Validar la contraseña con los validadores de Django y crear la cuenta con `create_user()`. Para la web, usar sesiones de Django y protección CSRF en las operaciones de escritura. Limitar los campos editables del perfil a una lista explícita para impedir cambios de rol o privilegios desde ese formulario.

Probar el alta con cada rol, el rechazo de roles desconocidos, la edición del perfil propio y la imposibilidad de leer el teléfono ajeno desde usuarios o el foro. El acceso del repartidor elegido se define en la [guía de contacto](../contacto/README.md).
