from django.db import models


class Curso(models.Model):
    id = models.BigAutoField(primary_key=True)
    MODALIDAD = [
        ('PRESENCIAL', 'Presencial'),
        ('VIRTUAL', 'Virtual'),
    ]

    ESTADO = [
        ('PROGRAMADO', 'Programado'),
        ('CANCELADO', 'Cancelado'),
        ('FINALIZADO', 'Finalizado'),
    ]


    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    fecha = models.DateField()
    hora = models.TimeField()
    duracion_horas = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cupo_maximo = models.PositiveIntegerField()
    modalidad = models.CharField(max_length=20, choices=MODALIDAD)
    estado = models.CharField(max_length=20, choices=ESTADO, default='PROGRAMADO')


    def __str__(self):
        return self.nombre


class InscripcionCurso(models.Model):
    id = models.BigAutoField(primary_key=True)
    ESTADOS = [
        ('inscrita', 'Inscrita'),
        ('cancelada', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='inscripciones'
    )

    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name='inscripciones'
    )

    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='inscrita')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cliente', 'curso'],
                name='cliente_curso_unico'
            )
        ]

    def __str__(self):
        return f"{self.cliente} - {self.curso}"