from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum


class Factura(models.Model):
    id = models.BigAutoField(primary_key=True)

    ESTADO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('CANCELADA', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='facturas'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='PENDIENTE'
    )

    def __str__(self):
        return f"Factura {self.id}"


class DetalleFactura(models.Model):
    id = models.BigAutoField(primary_key=True)

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    producto = models.ForeignKey(
        'productos.Producto',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    curso = models.ForeignKey(
        'cursos.Curso',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    cantidad = models.PositiveIntegerField(default=1)

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"Detalle {self.id} - Factura {self.factura.id}"
    def clean(self):
        if bool(self.producto_id) == bool(self.curso_id):
            raise ValidationError('Seleccione un producto o un curso, no ambos.')
        if self.cantidad < 1:
            raise ValidationError('La cantidad debe ser mayor que cero.')
        if self.factura_id and self.factura.estado == 'CANCELADA':
            raise ValidationError('No se pueden agregar detalles a una factura cancelada.')
        if self.producto_id:
            if not self.producto.activo or self.producto.stock < self.cantidad:
                raise ValidationError('Producto inactivo o stock insuficiente.')
        if self.curso_id:
            if self.cantidad != 1 or self.curso.estado != 'PROGRAMADO':
                raise ValidationError('El curso debe estar programado y la cantidad debe ser 1.')
            if self.factura_id:
                from cursos.models import InscripcionCurso
                if not InscripcionCurso.objects.filter(
                    cliente_id=self.factura.cliente_id, curso_id=self.curso_id,
                    estado='inscrita'
                ).exists():
                    raise ValidationError('El cliente debe estar inscrito en el curso.')
                if DetalleFactura.objects.filter(
                    factura__cliente_id=self.factura.cliente_id, curso_id=self.curso_id
                ).exclude(factura__estado='CANCELADA').exclude(pk=self.pk).exists():
                    raise ValidationError('Este curso ya fue facturado al cliente.')

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Los detalles existentes no se editan: evita duplicar movimientos de inventario.
        if self.pk:
            raise ValidationError('No se pueden editar detalles existentes. Elimine y cree otro.')

        factura = Factura.objects.select_for_update().get(pk=self.factura_id)
        if factura.estado == 'CANCELADA':
            raise ValidationError('No se pueden agregar detalles a una factura cancelada.')

        self.full_clean(exclude=['precio_unitario', 'subtotal'])
        if self.producto_id:
            from productos.models import Producto
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)
            if not producto.activo or producto.stock < self.cantidad:
                raise ValidationError('Producto inactivo o stock insuficiente.')
            self.precio_unitario = producto.precio
            producto.stock -= self.cantidad
            producto.save(update_fields=['stock'])
        else:
            from cursos.models import Curso
            curso = Curso.objects.get(pk=self.curso_id)
            self.precio_unitario = curso.precio

        self.subtotal = (self.precio_unitario * self.cantidad).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)
        factura.total = (factura.total + self.subtotal).quantize(Decimal('0.01'))
        factura.save(update_fields=['total'])

    @transaction.atomic
    def delete(self, *args, **kwargs):
        factura = Factura.objects.select_for_update().get(pk=self.factura_id)
        if factura.estado != 'PENDIENTE':
            raise ValidationError('No se pueden eliminar detalles de facturas cerradas.')
        if self.producto_id:
            from productos.models import Producto
            producto = Producto.objects.select_for_update().get(pk=self.producto_id)
            producto.stock += self.cantidad
            producto.save(update_fields=['stock'])
        resultado = super().delete(*args, **kwargs)
        total = factura.detalles.aggregate(total=Sum('subtotal'))['total']
        factura.total = total if total is not None else Decimal('0.00')
        factura.save(update_fields=['total'])
        return resultado