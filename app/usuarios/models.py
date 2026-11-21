"""Modelos de usuarios."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Usuario(AbstractUser):
  rol = models.CharField(
    max_length=11,
    unique=True
  )
  celular = models.CharField(max_length=20)
  es_discapacitado = models.BooleanField(default=False)
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
  entregas_exitosas = models.PositiveIntegerField(
    null=True,
    blank=True
  )
  entregas_totales = models.PositiveIntegerField(
    null=True,
    blank=True
  )

  REQUIRED_FIELDS = ["rol", "Celular"]

  def __str__(self):
    return self.username
