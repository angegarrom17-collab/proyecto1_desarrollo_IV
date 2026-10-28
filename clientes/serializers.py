from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate_cedula(self, value):
        cedula_limpia = value.strip()
        if len(cedula_limpia) < 5:
            raise serializers.ValidationError('La cédula debe tener una longitud válida.')
        return cedula_limpia

 