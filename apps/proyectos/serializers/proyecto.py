from rest_framework import serializers

from apps.proyectos.models.proyecto import Proyecto


class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = (
            "id",
            "title",
            "description",
            "date_started",
            "is_completed",
            "date_completed",
            "user",
            "mandante",
            "image_url",
        )
        read_only_fields = ("id", "created_at", "updated_at")
