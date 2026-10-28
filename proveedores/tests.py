from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta
from productos.models import Categoria, Producto
from .models import Proveedor, EntradaProducto
from .serializers import ProveedorSerializer, EntradaProductoSerializer

class PruebasProveedores(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.proveedor = Proveedor.objects.create(nombre='Distribuidora', telefono='88887777', correo='proveedor@example.com', direccion='San Jose Costa Rica')
        categoria = Categoria.objects.create(nombre='Bases')
        self.producto = Producto.objects.create(nombre='Base liquida', categoria=categoria, precio=8000, stock=5, fecha_vencimiento=date.today()+timedelta(days=500), proveedor=self.proveedor)

    def test_listar_proveedores(self):
        self.assertEqual(self.api.get('/api/proveedores/').status_code, 200)

    def test_telefono_invalido(self):
        serializer = ProveedorSerializer(self.proveedor, data={'telefono': '123'}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_nombre_corto(self):
        serializer = ProveedorSerializer(self.proveedor, data={'nombre': 'A'}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_entrada_aumenta_stock(self):
        EntradaProducto.objects.create(proveedor=self.proveedor, producto=self.producto, cantidad=3)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)

    def test_entrada_cantidad_cero(self):
        serializer = EntradaProductoSerializer(data={'proveedor': self.proveedor.pk, 'producto': self.producto.pk, 'cantidad': 0})
        self.assertFalse(serializer.is_valid())

    def test_proveedor_inactivo_no_recibe_entrada(self):
        self.proveedor.activo = False
        self.proveedor.save()
        serializer = EntradaProductoSerializer(data={'proveedor': self.proveedor.pk, 'producto': self.producto.pk, 'cantidad': 2})
        self.assertFalse(serializer.is_valid())