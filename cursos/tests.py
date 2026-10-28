from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta, time
from clientes.models import Cliente
from .models import Curso, InscripcionCurso
from .serializers import CursoSerializer, InscripcionCursoSerializer

class PruebasCursos(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.cliente = Cliente.objects.create(cedula='123456', nombre='Ana', email='ana@example.com')
        self.curso = Curso.objects.create(nombre='Maquillaje', descripcion='Basico', fecha=date.today()+timedelta(days=30), hora=time(10,0), duracion_horas=2, precio=10000, cupo_maximo=1, modalidad='VIRTUAL', estado='PROGRAMADO')

    def test_listar_cursos(self):
        self.assertEqual(self.api.get('/api/cursos/').status_code, 200)

    def test_precio_cero(self):
        serializer = CursoSerializer(self.curso, data={'precio': 0}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_cupo_cero(self):
        serializer = CursoSerializer(self.curso, data={'cupo_maximo': 0}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_inscripcion_valida(self):
        serializer = InscripcionCursoSerializer(data={'cliente': self.cliente.pk, 'curso': self.curso.pk, 'estado': 'inscrita'})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(InscripcionCurso.objects.count(), 1)

    def test_curso_sin_cupo(self):
        InscripcionCurso.objects.create(cliente=self.cliente, curso=self.curso)
        otro = Cliente.objects.create(cedula='654321', nombre='Luis', email='luis@example.com')
        serializer = InscripcionCursoSerializer(data={'cliente': otro.pk, 'curso': self.curso.pk})
        self.assertFalse(serializer.is_valid())

    def test_cliente_inactivo_no_se_inscribe(self):
        self.cliente.activo = False
        self.cliente.save()
        serializer = InscripcionCursoSerializer(data={'cliente': self.cliente.pk, 'curso': self.curso.pk})
        self.assertFalse(serializer.is_valid())