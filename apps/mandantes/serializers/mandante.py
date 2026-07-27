from rest_framework import serializers

from apps.mandantes.models.mandante import Contacto, Mandante


class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = ("id", "name", "email", "phone", "cargo", "position", "details", "mandante")
        read_only_fields = ("id", "created_at", "updated_at")


class MandanteSerializer(serializers.ModelSerializer):
    contactos = ContactoSerializer(many=True, read_only=True)

    class Meta:
        model = Mandante
        fields = ("id", "name", "location", "details", "contactos")
        read_only_fields = ("id", "created_at", "updated_at")
