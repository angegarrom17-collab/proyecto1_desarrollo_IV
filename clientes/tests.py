from django.test import TestCase
from rest_framework.test import APIClient
from .models import Cliente
from .serializers import ClienteSerializer
from django.contrib.auth.models import User

class PruebasClientes(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.usuario = User.objects.create_superuser(username='tienda_belleza_user',password='Belleza2026!')
        self.api.force_authenticate(user=self.usuario)
        self.datos = {'cedula': '123456789', 'nombre': 'Ana Solis', 'email': 'ana@example.com'}

    def test_crear_cliente(self):
        respuesta = self.api.post('/api/clientes/', self.datos, format='json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertTrue(Cliente.objects.filter(cedula='123456789').exists())

    def test_listar_clientes(self):
        Cliente.objects.create(**self.datos)
        self.assertEqual(self.api.get('/api/clientes/').status_code, 200)

    def test_cedula_corta(self):
        datos = {**self.datos, 'cedula': '123'}
        self.assertFalse(ClienteSerializer(data=datos).is_valid())

    def test_cedula_duplicada(self):
        Cliente.objects.create(**self.datos)
        self.assertFalse(ClienteSerializer(data={**self.datos, 'email': 'otra@example.com'}).is_valid())

    def test_cliente_inexistente(self):
        self.assertEqual(self.api.get('/api/clientes/999999/').status_code, 404)