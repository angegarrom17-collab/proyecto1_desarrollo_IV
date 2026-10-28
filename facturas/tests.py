from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from clientes.models import Cliente
from productos.models import Categoria, Producto
from .models import Factura, DetalleFactura
from django.contrib.auth.models import User

class PruebasFacturas(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.usuario = User.objects.create_superuser(username='tienda_belleza_user',password='Belleza2026!')
        self.api.force_authenticate(user=self.usuario)
        self.cliente = Cliente.objects.create(cedula='123456', nombre='Ana', email='ana@example.com')
        categoria = Categoria.objects.create(nombre='Sombras')
        self.producto = Producto.objects.create(nombre='Sombra', categoria=categoria, precio=3000, stock=10, fecha_vencimiento=date.today()+timedelta(days=500))
        self.factura = Factura.objects.create(cliente=self.cliente, estado='PENDIENTE')

    def test_crear_factura(self):
        self.assertEqual(Factura.objects.count(), 1)
        self.assertEqual(self.factura.estado, 'PENDIENTE')

    def test_listar_facturas(self):
        self.assertEqual(self.api.get('/api/facturas/').status_code, 200)

    def test_detalle_sin_producto_ni_curso(self):
        detalle = DetalleFactura(factura=self.factura, cantidad=1, precio_unitario=1, subtotal=1)
        with self.assertRaises(ValidationError):
            detalle.clean()

    def test_detalle_cantidad_cero(self):
        detalle = DetalleFactura(factura=self.factura, producto=self.producto, cantidad=0, precio_unitario=3000, subtotal=0)
        with self.assertRaises(ValidationError):
            detalle.clean()

    def test_factura_cancelada_no_admite_detalle(self):
        self.factura.estado = 'CANCELADA'
        self.factura.save()
        detalle = DetalleFactura(factura=self.factura, producto=self.producto, cantidad=1, precio_unitario=3000, subtotal=3000)
        with self.assertRaises(ValidationError):
            detalle.clean()

    def test_stock_insuficiente(self):
        detalle = DetalleFactura(factura=self.factura, producto=self.producto, cantidad=20, precio_unitario=3000, subtotal=60000)
        with self.assertRaises(ValidationError):
            detalle.clean()