# Cancelaciones de ayuda aceptada

El autor de una publicación podrá solicitar la cancelación de una ayuda activa indicando el motivo. La cancelación solo será efectiva con el consentimiento del autor y del repartidor asignado.

## Implementación propuesta

1. Crear `SolicitudCancelacion` vinculada a la ayuda, con justificación, estado y fechas de decisión de ambos participantes. Permitir una sola solicitud pendiente por ayuda. Validar la justificación después de quitar espacios y rechazar el texto vacío.
2. En `POST /api/v1/cancelaciones/`, comprobar que quien solicita es el autor y que la ayuda está activa. Proponer en la interfaz una acción explícita «Aprobar y solicitar cancelación» que registre el consentimiento del autor al enviar la justificación. Dejar la decisión del repartidor pendiente y avisarle en privado.
3. En `POST /api/v1/cancelaciones/<id>/decision/`, aceptar aprobación o rechazo del repartidor asignado. Determinar su identidad desde la sesión. Mostrarle la misma justificación que aprobó el autor y conservarla sin ediciones durante la decisión.
4. Procesar la decisión en una transacción, comprobando de nuevo la ayuda y el estado pendiente. Con ambas aprobaciones, marcar la ayuda cancelada, cerrar el acceso al contacto y avisar a ambos. Si el repartidor rechaza, registrar el rechazo, mantener la ayuda activa y avisar al autor. Una solicitud pendiente por sí sola conserva la asignación.
5. Como decisión de diseño propuesta, mantener cerrada la publicación tras cancelar. El autor puede eliminarla o publicar otra solicitud. Los candidatos descartados conservan ese estado.

## Comprobaciones

Cubrir motivo vacío, aprobación de un tercero, rechazo y doble envío de la decisión. Validar que una persona no pueda aportar los dos consentimientos, que los reintentos no dupliquen avisos y que completar y cancelar simultáneamente produzca un único estado final.
