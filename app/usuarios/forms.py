from uuid import uuid4

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class FotoPerfilForm(forms.Form):
    foto_perfil = forms.ImageField(
        label="Foto de perfil",
        help_text="Elige una imagen JPG, PNG o WebP de hasta 5 MB.",
        widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
    )

    def clean_foto_perfil(self):
        foto = self.cleaned_data["foto_perfil"]
        extensiones = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}
        if foto.image.format not in extensiones:
            raise forms.ValidationError("Elige una imagen JPG, PNG o WebP.")
        if foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError("La foto debe pesar como máximo 5 MB.")
        foto.name = f"{uuid4().hex}.{extensiones[foto.image.format]}"
        return foto


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
