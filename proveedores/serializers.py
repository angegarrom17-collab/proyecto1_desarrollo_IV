from rest_framework import serializers
from .models import Proveedor, EntradaProducto

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def validate_nombre(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return value.strip()

    def validate_telefono(self, value):
        if len(value) != 8 or not value.isdigit():
            raise serializers.ValidationError('El teléfono debe tener 8 números.')
        return value

    def validate_direccion(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('La dirección debe tener al menos 10 caracteres.')
        return value.strip()

class EntradaProductoSerializer(serializers.ModelSerializer):
    
    nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = EntradaProducto
        fields = '__all__'
        read_only_fields = ['fecha']

    def validate(self, data):
        proveedor = data.get('proveedor')
        producto = data.get('producto')
        cantidad = data.get('cantidad')
        if proveedor and not proveedor.activo:
            raise serializers.ValidationError('El proveedor debe estar activo.')
        if producto and proveedor and producto.proveedor_id != proveedor.id:
            raise serializers.ValidationError('El producto debe pertenecer al proveedor seleccionado.')
        if cantidad is not None and cantidad <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor que cero.')
        return data