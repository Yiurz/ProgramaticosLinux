# Contacto privado de la entrega

El repartidor elegido podrá consultar el medio de contacto que la persona solicitante haya compartido para acordar lugar y horario de entrega. La coordinación puede continuar por ese medio.

## Implementación propuesta

1. Acordar con usuarios qué campo compartirá el autor para la entrega, por ejemplo su teléfono o correo. Indicarle al publicar quién podrá verlo después de la aprobación y validar que el medio elegido tenga un valor.
2. Definir la consulta `GET /api/v1/contacto/<ayuda_id>/`. Recuperar la ayuda activa filtrando por el repartidor autenticado y la asignación aprobada. Obtener al autor desde esa misma publicación para evitar que el cliente pueda consultar otros perfiles por identificador.
3. Construir la respuesta con el medio elegido y su valor. Mantener esos campos fuera de las publicaciones, listados de postulantes, notificaciones y registros de peticiones. Indicar al cliente que evite almacenar la respuesta en cachés compartidas mediante `Cache-Control: private, no-store`.
4. Revalidar el acceso en cada lectura. La propuesta mantiene la coordinación mientras la cancelación esté pendiente y finaliza el acceso cuando la ayuda quede cancelada o completada.

## Comprobaciones

Verificar el acceso del elegido tras la aprobación. Probar también con una sesión anónima, un candidato pendiente, uno descartado y un repartidor asignado a otra entrega. Tras una cancelación confirmada, una consulta nueva debe dejar de devolver los datos. [Asignación de la ayuda](../postulaciones/README.md)
