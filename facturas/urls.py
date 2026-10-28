from django.urls import path
from . import views

urlpatterns = [
    path('', views.facturas_api, name='facturas'),
    path('estadisticas/', views.estadisticas_facturacion_api, name='estadisticas_facturacion'),
    path('<int:id>/', views.factura_detalle_api, name='factura_detalle'),
    path('<int:id>/detalles/', views.detalles_factura_api, name='detalles_factura'),
    path('detalles/<int:id>/', views.detalle_factura_api, name='detalle_factura'),
]