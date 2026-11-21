"""Registro, inicio y perfil de usuario."""
from functools import partial

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.translation import override
from django.views.decorators.http import require_http_methods

from .forms import FotoPerfilForm, RegistroForm
from .models import Usuario


@require_http_methods(["GET", "POST"])
@override("es")
def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    form = RegistroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        return redirect("inicio")

    return render(request, "usuarios/registro.html", {"form": form})


@login_required
def inicio(request):
    return render(request, "usuarios/inicio.html")


@login_required
@require_http_methods(["GET", "POST"])
@override("es")
def perfil(request):
    if request.method == "POST":
        form = FotoPerfilForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                usuario = Usuario.objects.select_for_update().get(pk=request.user.pk)
                anterior = usuario.foto_perfil
                usuario.foto_perfil = form.cleaned_data["foto_perfil"]
                usuario.save(update_fields=["foto_perfil"])
                if anterior:
                    transaction.on_commit(partial(anterior.storage.delete, anterior.name))
            messages.success(request, "Tu foto de perfil se ha actualizado.")
            return redirect("usuarios:perfil")
    else:
        form = FotoPerfilForm()
    return render(request, "usuarios/perfil.html", {"form": form})

