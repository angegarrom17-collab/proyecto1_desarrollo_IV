from django.db import models

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    
    VIGENCIA_CHOICES = [
        (12, '12 Meses (1 Año)'),
        (24, '24 Meses (2 Años)'),
        (36, '36 Meses (3 Años)'),
    ]

    id = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    proveedor = models.ForeignKey('proveedores.Proveedor', on_delete=models.PROTECT, related_name='productos', null=True, blank=True)
    
    
    vigencia_meses = models.IntegerField(
        choices=VIGENCIA_CHOICES,
        default=12
    )
    fecha_vencimiento = models.DateField()
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre