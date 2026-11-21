# Calificaciones de repartidores

La persona que recibió una entrega podrá calificar al repartidor asignado. La reputación permitirá al autor de otra publicación consultar la experiencia previa al elegir entre candidatos.

## Implementación propuesta

1. Se propone una escala entera de 1 a 5 y una calificación por entrega completada. Crear `Calificacion` con referencia única a la ayuda, puntaje y fecha. Aplicar el rango tanto en la validación de entrada como con una restricción de base de datos.
2. En `POST /api/v1/calificaciones/`, recibir ayuda y puntaje. Comprobar que la ayuda está completada y pertenece al autor autenticado. Obtener el repartidor desde la asignación para impedir que el cliente puntúe a otra persona.
3. En `GET /api/v1/calificaciones/repartidores/<id>/`, calcular promedio y cantidad a partir de las calificaciones persistidas. Para un repartidor nuevo devolver cantidad cero y promedio nulo, de modo que la interfaz pueda mostrar «Sin calificaciones».
4. Reutilizar la consulta del resumen en el listado de candidatos. Agrupar por repartidor cuando se consulten varios y devolver únicamente promedio y cantidad.

## Comprobaciones

Probar los extremos 1 y 5, los puntajes fuera de rango y dos intentos para la misma ayuda. Verificar que las entregas activas o canceladas y las de otros autores no admitan calificación. Con dos entregas puntuadas con 3 y 5 para el mismo repartidor, el resumen debe indicar promedio 4 y cantidad 2.
