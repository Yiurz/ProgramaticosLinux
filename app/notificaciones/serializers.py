from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            "id",
            "destinatario",
            "usuario_origen",
            "evento_id",
            "tipo",
            "mensaje",
            "fecha",
            "leida",
        ]
        read_only_fields = fields
