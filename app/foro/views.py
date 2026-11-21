from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Exists, F, OuterRef
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from notificaciones.services import crear_notificacion
from pedidos.gestor import GestorPedidos
from pedidos.models import Pedido, SolicitudCancelacion
from postulaciones.models import Postulacion, Publicacion
from postulaciones.services import ofrecer_ayuda
from usuarios.models import Usuario


class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ("titulo", "descripcion")
        labels = {"titulo": "¿Qué necesitas?", "descripcion": "Detalles del pedido"}
        widgets = {
            "titulo": forms.TextInput(attrs={"placeholder": "Por ejemplo, un almuerzo"}),
            "descripcion": forms.Textarea(attrs={"rows": 4, "placeholder": "Indica qué recoger y en qué sector del campus."}),
        }


def publicaciones_activas(usuario):
    return usuario.publicaciones.exclude(estado=Publicacion.Estado.ELIMINADA)


def mostrar_foro(request, form=None):
    usuario = request.user
    pedidos = Pedido.objects.filter(estado=Pedido.Estado.ACTIVO).select_related("publicacion", "cliente", "repartidor")
    contexto = {"avisos": usuario.notificaciones.all()[:30], "sin_leer": usuario.notificaciones.filter(leida=False).count()}
    if usuario.tipo_usuario == Usuario.Tipos.DISCAPACITADO:
        publicacion = publicaciones_activas(usuario).order_by("-pk").first()
        contexto.update(es_autor=True, propia=publicacion, form=form or PublicacionForm(),
                        pedido=pedidos.filter(cliente=usuario).first())
        if publicacion:
            contexto["candidatos"] = publicacion.postulaciones.filter(
                estado__in=(Postulacion.Estado.PENDIENTE, Postulacion.Estado.EN_ESPERA)
            ).select_related("repartidor").order_by("fecha")
    elif usuario.tipo_usuario == Usuario.Tipos.REPARTIDOR:
        contexto["pedido"] = pedidos.filter(repartidor=usuario).first()
        contexto["publicaciones"] = Publicacion.objects.filter(estado=Publicacion.Estado.ABIERTA).select_related("autor").annotate(
            ofrecida=Exists(usuario.postulaciones_enviadas.filter(publicacion=OuterRef("pk"), estado__in=Postulacion.ESTADOS_VIGENTES))
        ).order_by("-fecha_creacion")
    else:
        raise PermissionDenied
    return render(request, "foro/tablon.html", contexto)


@login_required
def tablon(request):
    return mostrar_foro(request)


@login_required
@require_POST
def publicar(request):
    if request.user.tipo_usuario != Usuario.Tipos.DISCAPACITADO:
        raise PermissionDenied
    form = PublicacionForm(request.POST)
    if not form.is_valid():
        return mostrar_foro(request, form)
    with transaction.atomic():
        autor = Usuario.objects.select_for_update().get(pk=request.user.pk)
        if publicaciones_activas(autor).exists():
            messages.error(request, "Ya tienes una publicación activa.")
        else:
            publicacion = form.save(commit=False)
            publicacion.autor = autor
            publicacion.save()
            Usuario.objects.filter(pk=autor.pk).update(tiene_pub_activa=True)
    return redirect("tablon")


@login_required
@require_POST
def ofrecer(request, pk):
    try:
        ofrecer_ayuda(pk, request.user)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    return redirect("tablon")


@login_required
@require_POST
def elegir(request, pk):
    get_object_or_404(Postulacion, pk=pk, publicacion__autor=request.user)
    try:
        GestorPedidos.iniciar_pedido(pk, request.user)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    return redirect("tablon")


@login_required
@require_POST
@transaction.atomic
def entregar(request, pk):
    if request.user.tipo_usuario != Usuario.Tipos.REPARTIDOR:
        raise PermissionDenied
    pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pk, repartidor=request.user)
    if pedido.estado != Pedido.Estado.ACTIVO:
        return redirect("tablon")
    if pedido.cancelaciones.filter(estado=SolicitudCancelacion.Estado.PENDIENTE).exists():
        messages.error(request, "Resuelvan la cancelación pendiente antes de confirmar la entrega.")
        return redirect("tablon")
    pedido.estado = Pedido.Estado.COMPLETADO
    pedido.entrega_confirmada = True
    pedido.fecha_fin = timezone.now()
    pedido.save(update_fields=["estado", "entrega_confirmada", "fecha_fin"])
    pedido.publicacion.estado = Publicacion.Estado.ELIMINADA
    pedido.publicacion.save(update_fields=["estado"])
    Usuario.objects.filter(pk=pedido.cliente_id).update(tiene_pub_activa=False)
    Usuario.objects.filter(pk=request.user.pk).update(entregas_totales=Coalesce(F("entregas_totales"), 0) + 1)
    crear_notificacion(pedido.cliente, "ENTREGA_COMPLETADA", f"entrega-{pedido.pk}",
                       request.user, detalle=pedido.publicacion.titulo)
    messages.success(request, "Entrega completada. Ya puedes ofrecerte para otro pedido.")
    return redirect("tablon")


@login_required
@require_POST
def leer(request):
    request.user.notificaciones.filter(leida=False).update(leida=True)
    return redirect("tablon")
