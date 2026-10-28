from django.contrib import admin
from .models import EntradaProducto, Proveedor

admin.site.register(Proveedor)

@admin.register(EntradaProducto)
class EntradaProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'proveedor', 'producto', 'cantidad', 'fecha']