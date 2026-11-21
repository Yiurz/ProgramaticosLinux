# Foro de solicitudes

La publicación describe qué necesita la persona, dónde se coordinará la entrega en el campus y si aún recibe ofrecimientos. Su autoría determina quién puede elegir al repartidor y eliminar la publicación.

## Implementación propuesta

1. Definir `Publicacion` con autor, título, descripción del pedido, sector del campus, fecha y estado de convocatoria. Asignar `abierta` al crear. Reservar el punto exacto de encuentro y el contacto personal para la coordinación privada.
2. En `POST /api/v1/foro/`, exigir el rol `discapacitado`, tomar el autor de la sesión y validar los campos del pedido. En `GET /api/v1/foro/`, listar las solicitudes abiertas. Permitir al autor consultar sus publicaciones cerradas en su historial.
3. En el detalle `GET /api/v1/foro/<id>/`, exponer el estado y una representación pública del autor. El listado de candidatos para elegir corresponde a postulaciones y es privado para el autor.
4. Al aprobar un candidato, cambiar la convocatoria a `cerrada` en la misma transacción que registra la asignación. Mantener por separado el estado de la ayuda para distinguir una publicación cerrada de una entrega completada.
5. Para `DELETE /api/v1/foro/<id>/`, comprobar autoría. Como propuesta, marcarla como eliminada y retirarla del foro conservando las referencias para el historial. Si existe ayuda en curso, exigir primero la cancelación bilateral para que eliminar la publicación no interrumpa unilateralmente la entrega. Al eliminar una solicitud abierta, invalidar sus postulaciones pendientes en la misma operación.

## Comprobaciones

Probar que un repartidor puede ver una solicitud abierta y ofrecerse desde postulaciones, que otro autor no puede eliminarla y que una solicitud eliminada deja de admitir candidatos. Probar también la eliminación simultánea con una postulación o aprobación. [Flujo de aprobación](../postulaciones/README.md)
