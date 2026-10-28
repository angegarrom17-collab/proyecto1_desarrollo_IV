from rest_framework import serializers
from .models import Factura, DetalleFactura


class FacturaSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.CharField(source="cliente.nombre", read_only=True)
    detalles = serializers.SerializerMethodField()

    def get_detalles(self, obj):
        return [{"id": d.id, "producto": d.producto.nombre if d.producto else "Ninguno", "curso": d.curso.nombre if d.curso else "Ninguno", "cantidad": d.cantidad, "subtotal": d.subtotal} for d in obj.detalles.select_related("producto", "curso").all()]

    class Meta:
        model = Factura
        fields = '__all__'
        read_only_fields = ['id', 'fecha', 'total']

    def validate(self, data):
        cliente = data.get('cliente')
        total = data.get('total')

        if cliente and not cliente.activo:
            raise serializers.ValidationError({
                'cliente': 'El cliente debe estar activo.'
            })

        if total is not None and total < 0:
            raise serializers.ValidationError({
                'total': 'El total no puede ser negativo.'
            })

        return data


class DetalleFacturaSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.CharField(source="factura.cliente.nombre", read_only=True)
    nombre_producto = serializers.CharField(source="producto.nombre", read_only=True, default="Ninguno")
    nombre_curso = serializers.CharField(source="curso.nombre", read_only=True, default="Ninguno")

    class Meta:
        model = DetalleFactura
        fields = '__all__'
        read_only_fields = ['id', 'precio_unitario', 'subtotal']

    def validate(self, data):
        producto = data.get('producto')
        curso = data.get('curso')
        cantidad = data.get('cantidad')
        precio_unitario = data.get('precio_unitario')
        subtotal = data.get('subtotal')

        if producto and curso:
            raise serializers.ValidationError(
                'Debe seleccionar un producto o un curso, no ambos.'
            )

        if not producto and not curso and not self.instance:
            raise serializers.ValidationError(
                'Debe seleccionar un producto o un curso.'
            )

        if cantidad is not None and cantidad <= 0:
            raise serializers.ValidationError({
                'cantidad': 'La cantidad debe ser mayor que cero.'
            })

        if precio_unitario is not None and precio_unitario <= 0:
            raise serializers.ValidationError({
                'precio_unitario': 'El precio debe ser mayor que cero.'
            })

        if subtotal is not None and subtotal < 0:
            raise serializers.ValidationError({
                'subtotal': 'El subtotal no puede ser negativo.'
            })

        if producto and not producto.activo:
            raise serializers.ValidationError({
                'producto': 'El producto debe estar activo.'
            })

        if producto and cantidad is not None:
            if cantidad > producto.stock:
                raise serializers.ValidationError({
                    'cantidad': 'No hay suficiente stock disponible.'
                })

        if curso and curso.estado != 'PROGRAMADO':
            raise serializers.ValidationError({
                'curso': 'El curso debe estar programado.'
            })

        return data