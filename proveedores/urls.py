from django.urls import path
from . import views
urlpatterns = [
    path('', views.proveedores_api, name='proveedores_api' ),
    path('entradas/', views.entradas_api, name='entradas_api'),
    path('entradas/<int:id>/', views.entrada_detalle_api, name='entrada_detalle_api'),
    path('<int:id>/', views.proveedor_detalle_api, name='proveedor_detalle_api'),
]