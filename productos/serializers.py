from datetime import date, timedelta
from rest_framework import serializers
from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Categoria
        fields = '__all__'

    def validate_nombre(self, value):
        nombre_limpio = value.strip()
        if len(nombre_limpio) < 2:
            raise serializers.ValidationError('El nombre de la categoría debe tener al menos 2 caracteres.')
        return nombre_limpio


class ProductoSerializer(serializers.ModelSerializer):
   
    categoria_detalle = CategoriaSerializer(source='categoria', read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'

    def validate_nombre(self, value):
        nombre_limpio = value.strip()
        if len(nombre_limpio) < 2:
            raise serializers.ValidationError('El nombre del producto debe tener al menos 2 caracteres.')
        return nombre_limpio

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor que cero.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value

    def validate(self, data):
        proveedor = data.get("proveedor")
        if proveedor and not proveedor.activo:
            raise serializers.ValidationError({"proveedor": "El proveedor debe estar activo."})
        if data.get("stock_minimo", 0) < 0:
            raise serializers.ValidationError({"stock_minimo": "No puede ser negativo."})
        fecha_vencimiento = data.get('fecha_vencimiento')
        
        vigencia_meses = data.get('vigencia_meses')
        if vigencia_meses is None and self.instance:
            vigencia_meses = self.instance.vigencia_meses
        elif vigencia_meses is None:
            vigencia_meses = 12

        
        dias_requeridos = vigencia_meses * 30
        fecha_minima_permitida = date.today() + timedelta(days=dias_requeridos)

        if fecha_vencimiento and fecha_vencimiento < fecha_minima_permitida:
            raise serializers.ValidationError({
                'fecha_vencimiento': f'La fecha de vencimiento debe tener al menos {vigencia_meses} meses de vigencia a partir de hoy.'
            })

        return data