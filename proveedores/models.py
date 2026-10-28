from django.db import models, transaction
from django.db.models import F

class Proveedor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=8)
    correo = models.EmailField(unique=True)
    direccion = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class EntradaProducto(models.Model):
    id = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='entradas')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, related_name='entradas')
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entrada {self.id} - {self.producto}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                old_instance = EntradaProducto.objects.get(pk=self.pk)
                diferencia = self.cantidad - old_instance.cantidad
                if diferencia != 0:
                    self.producto.__class__.objects.filter(pk=self.producto_id).update(stock=F('stock') + diferencia)
            else:
                self.producto.__class__.objects.filter(pk=self.producto_id).update(stock=F('stock') + self.cantidad)
            
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.producto.__class__.objects.filter(pk=self.producto_id).update(stock=F('stock') - self.cantidad)
            super().delete(*args, **kwargs)