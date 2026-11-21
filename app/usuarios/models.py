"""Modelos de usuarios."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Usuario(AbstractUser):
  rut_id = models.CharField(
    max_length=11,
    unique=True
  )
  celular = models.CharField(max_length=20)
  es_verificado = models.BooleanField(default=False)
  tiene_pub_activa = models.BooleanField(default=False)
  rating = models.DecimalField(
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(0),
      MaxValueValidator(5)
    ],
    null=True,
    blank=True
  )
  entregas_totales = models.PositiveIntegerField(
    null=True,
    blank=True
  )
  penalizado = models.BooleanField(default=False)

  # Campos ignorados, no se usarán al final
  email = models.EmailField(null=True, blank=True)

  class Tipos(models.TextChoices):
    DISCAPACITADO = "DISCAPACITADO", "discapacitado"
    REPARTIDOR = "REPARTIDOR", "repartidor"
  tipo_usuario = models.CharField(choices=Tipos, default=Tipos.REPARTIDOR)

  REQUIRED_FIELDS = ["rut_id", "celular"]

  def __str__(self):
    return self.username
