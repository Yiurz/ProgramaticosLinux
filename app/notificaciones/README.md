# Notificaciones de estado

Este módulo comunicará los cambios de una publicación y de la ayuda asignada. Se propone una bandeja interna como primer canal y el correo como canal adicional configurable.

## Implementación propuesta

1. Acordar con los módulos que cambian el estado qué evento generan y quién debe recibirlo.

   | Cambio confirmado | Destinatarios |
   | --- | --- |
   | Nuevo ofrecimiento | Autor de la publicación |
   | Elección de repartidor y cierre del foro | Autor, elegido y cada descartado con su propio resultado |
   | Solicitud de cancelación | Repartidor asignado |
   | Cancelación aprobada o rechazada | Autor y repartidor asignado |
   | Entrega completada | Autor y repartidor asignado |

2. Definir `Notificacion` con destinatario, identificador del evento, tipo, referencia a la publicación o ayuda, fecha y fecha de lectura opcional. Crear los avisos de bandeja dentro de la transacción del cambio. Una restricción única por evento y destinatario evita duplicados en reintentos.
3. Implementar `GET /api/v1/notificaciones/` con filtro por usuario de sesión y orden de más reciente a más antiguo. En `POST /api/v1/notificaciones/<id>/leer/`, aplicar el mismo filtro y conservar la primera fecha de lectura al repetir la petición.
4. Para correo, registrar el envío pendiente en la misma transacción y activar su procesamiento después del commit. Guardar resultado e intentos para poder reintentar fallos. Usar el backend de consola ya configurado durante el desarrollo. El mensaje puede indicar el cambio y enlazar al detalle autenticado. Omitir teléfonos, correos de terceros y motivos privados.

## Comprobaciones

Simular una aprobación revertida y verificar que no genera avisos. Con varios candidatos, comprobar que cada uno ve únicamente su resultado y que el autor recibe el cierre. Probar aislamiento de bandejas, marcado repetido como leído y fallo de correo con la notificación interna aún disponible.
