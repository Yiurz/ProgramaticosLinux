# Postulaciones y asignación de ayuda

Este módulo vincula una publicación con los repartidores que se ofrecen. El autor de la solicitud elige a uno. La asignación resultante identifica a las dos personas autorizadas para coordinar la entrega.

## Implementación propuesta

1. Modelar `Postulacion` con publicación, repartidor, fecha y estado (pendiente, aprobada o descartada). Exigir unicidad del par publicación–repartidor. Modelar la ayuda asignada con una referencia única a la publicación y una referencia a la postulación elegida.
2. En `POST /api/v1/postulaciones/`, tomar el repartidor de la sesión, validar su rol y recibir el identificador de la publicación. Comprobar dentro de la operación de escritura que la convocatoria sigue abierta. En `GET /api/v1/postulaciones/?publicacion=<id>`, verificar la autoría antes de listar candidatos. Incluir la reputación del candidato cuando esté disponible.
3. En `POST /api/v1/postulaciones/<id>/aprobar/`, verificar que el usuario es autor de esa publicación y que la postulación pertenece a ella y sigue pendiente. Usar `transaction.atomic()` y una actualización condicionada a que la publicación siga abierta. Solo quien consiga cambiarla a cerrada puede crear la asignación, aprobar esa postulación y descartar todas las demás pendientes. Si falla cualquier escritura, revertir el conjunto.
4. Coordinar todas las altas de postulaciones y aprobaciones sobre la misma publicación para evitar candidatos tardíos. En un motor con bloqueo de filas, bloquear primero la publicación en ambas operaciones. En SQLite, donde `select_for_update()` carece de efecto, serializar mediante una escritura condicional previa y gestionar los conflictos de escritura reintentando la transacción completa. Una segunda elección distinta debe producir un conflicto.
5. Con la asignación confirmada, habilitar contacto y generar los avisos del cambio. Para el cierre de la entrega, se propone que el autor confirme la recepción con `POST /api/v1/postulaciones/<id>/completar/` sobre la postulación aprobada. Pasar la ayuda de activa a completada cuando no exista una cancelación pendiente y habilitar la calificación.

## Comprobaciones

Probar dos candidatos y dos aprobaciones simultáneas. Debe existir una única asignación y todos los demás candidatos deben quedar descartados. Repetir la misma aprobación debe devolver la asignación existente sin duplicar avisos. Probar además un ofrecimiento que llega durante el cierre y un intento de aprobar realizado por otro usuario.
