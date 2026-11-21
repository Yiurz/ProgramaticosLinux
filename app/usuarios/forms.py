from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroForm(UserCreationForm):
    tipo_usuario = forms.ChoiceField(
        label="Tipo de cuenta",
        choices=[
            ("", "Selecciona tu tipo de cuenta"),
            (Usuario.Tipos.DISCAPACITADO, "Persona con discapacidad"),
            (Usuario.Tipos.REPARTIDOR, "Repartidor"),
        ],
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "tipo_usuario", "rut_id", "celular")
        labels = {
            "username": "Nombre de usuario",
            "rut_id": "RUT",
            "celular": "Número de celular",
        }
        help_texts = {
            "username": "Lo usarás para iniciar sesión.",
            "rut_id": "Escríbelo sin puntos y con guion.",
        }
        widgets = {
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
            "celular": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
        }
