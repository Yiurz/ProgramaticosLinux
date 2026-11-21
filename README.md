# Proyecto de hackatón · Universidad Técnica Federico Santa María
Grupo: Programáticos
Renato Fernández
Soffia Romero
Axius Altamirano

Aplicación de campus para que personas con discapacidad soliciten entregas de alimentos y otros artículos, elijan un repartidor y coordinen la entrega en privado.

## Módulos de la API

Cada aplicación tiene su propio espacio de nombres bajo `/api/v1/<módulo>/`. Los prefijos están registrados con listas de rutas vacías. Los métodos y rutas en las guías son propuestas para la etapa de implementación.

| Módulo | Responsabilidad |
| --- | --- |
| [usuarios](app/usuarios/README.md) | Identidad, roles y perfil de contacto |
| [foro](app/foro/README.md) | Publicar, consultar y eliminar solicitudes |
| [postulaciones](app/postulaciones/README.md) | Ofrecer ayuda, elegir un repartidor y cerrar la convocatoria |
| [contacto](app/contacto/README.md) | Compartir los datos privados con el repartidor elegido |
| [cancelaciones](app/cancelaciones/README.md) | Justificación y acuerdo entre ambas partes |
| [calificaciones](app/calificaciones/README.md) | Puntaje y reputación del repartidor |
| [notificaciones](app/notificaciones/README.md) | Avisos de estado por bandeja interna o correo |

## Preparar el entorno

Desde la raíz del repositorio, con Python compatible con Django 6.1, ejecutar en Linux o macOS

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
cd app
python manage.py check
```

Para iniciar el servidor local, ejecutar `python manage.py runserver` desde `app/`. Un 404 al consultar uno de los prefijos es el resultado esperado en esta etapa.

## Orden de trabajo

1. Definir primero el usuario personalizado y su migración inicial **antes del primer migrate**, siguiendo la guía de usuarios. Los demás modelos podrán relacionarse con ese usuario.
2. Acordar los estados de publicación y ayuda entre foro y postulaciones. Cerrar la convocatoria significa que ya hay repartidor elegido. La entrega todavía puede estar en curso.
3. Usar la asignación confirmada como referencia compartida para contacto, cancelaciones y calificaciones. Notificaciones consume los cambios confirmados y los comunica a sus destinatarios.
4. En cada módulo, agregar los modelos en `models.py`, las vistas en `views.py` y sus rutas relativas en `urls.py`. Tras un cambio de esquema, generar y revisar la migración del módulo. Ejecutar `python manage.py test` desde `app/` al incorporar pruebas.
