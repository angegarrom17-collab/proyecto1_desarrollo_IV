from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer

class PruebasProductos(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.categoria = Categoria.objects.create(nombre='Labiales')
        self.datos = {'nombre': 'Labial rojo', 'categoria': self.categoria.pk, 'precio': '5000.00', 'stock': 10, 'stock_minimo': 2, 'vigencia_meses': 12, 'fecha_vencimiento': str(date.today()+timedelta(days=500))}

    def test_producto_valido(self):
        serializer = ProductoSerializer(data=self.datos)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(Producto.objects.count(), 1)

    def test_precio_negativo(self):
        serializer = ProductoSerializer(data={**self.datos, 'precio': '-1.00'})
        self.assertFalse(serializer.is_valid())

    def test_nombre_corto(self):
        serializer = ProductoSerializer(data={**self.datos, 'nombre': 'A'})
        self.assertFalse(serializer.is_valid())

    def test_vencimiento_insuficiente(self):
        serializer = ProductoSerializer(data={**self.datos, 'fecha_vencimiento': str(date.today()+timedelta(days=10))})
        self.assertFalse(serializer.is_valid())

    def test_categoria_nombre_corto(self):
        self.assertFalse(CategoriaSerializer(data={'nombre': 'A'}).is_valid())

    def test_listar_productos(self):
        self.assertEqual(self.api.get('/api/productos/').status_code, 200)