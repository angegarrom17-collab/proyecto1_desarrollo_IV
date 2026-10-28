from django import forms
from django.contrib import admin
from .models import Factura, DetalleFactura


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = '__all__'

    def clean(self):
        datos = super().clean()
        if (self.instance.pk and datos.get('estado') == 'CANCELADA'
                and self.instance.detalles.exists()):
            raise forms.ValidationError(
                'No se puede cancelar una factura que tiene detalles. '
                'Primero debe retirar sus detalles mediante la API.'
            )
        return datos


class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields = ['producto', 'curso', 'cantidad']

    def clean(self):
        datos = super().clean()
        if self.instance.pk and self.has_changed():
            raise forms.ValidationError('No se pueden modificar detalles guardados.')
        return datos


class DetalleFacturaInline(admin.TabularInline):
    model = DetalleFactura
    form = DetalleFacturaForm
    extra = 1
    can_delete = False
    fields = ['producto', 'curso', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['precio_unitario', 'subtotal']
    verbose_name = 'Producto o curso de la factura'
    verbose_name_plural = 'Productos y cursos de la factura'

    def has_add_permission(self, request, obj=None):
        if obj and obj.estado == 'CANCELADA':
            return False
        return super().has_add_permission(request, obj)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    form = FacturaForm
    list_display = ['id', 'cliente', 'fecha', 'estado', 'total']
    readonly_fields = ['fecha', 'total']
    inlines = [DetalleFacturaInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['cliente', 'fecha', 'total']
        return ['fecha', 'total']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ['id', 'factura', 'producto', 'curso', 'cantidad',
                    'precio_unitario', 'subtotal']
    readonly_fields = ['factura', 'producto', 'curso', 'cantidad',
                       'precio_unitario', 'subtotal']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False