"""Vistas de la API de usuarios."""
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import override

from .forms import RegistroForm


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

