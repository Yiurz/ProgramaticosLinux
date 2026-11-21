from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)


class Calificaciones(models.Model):

    pedido = models.OneToOneField(
        "pedidos.Pedido",
        on_delete=models.PROTECT,
        related_name="calificacion"
    )

    nueva_calificacion = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def actualizar_promedio(self):
        usuario = self.pedido.repartidor

        promedio = usuario.calificacion_promedio
        viajes = usuario.viajes_completados

        nuevo_promedio = (
            (promedio * viajes) + self.nueva_calificacion
        ) / (viajes + 1)

        usuario.calificacion_promedio = nuevo_promedio
        usuario.viajes_completados += 1

    def asignar_puntos(self):
        usuario = self.pedido.repartidor

        puntos_por_calificacion = {
            0: 0,
            1: 10,
            2: 20,
            3: 30,
            4: 40,
            5: 50
        }

        usuario.puntos += puntos_por_calificacion[
            self.nueva_calificacion
        ]

    def procesar_calificacion(self):
        self.actualizar_promedio()
        self.asignar_puntos()
        self.pedido.repartidor.save()