from django.urls import path
from . import views 

urlpatterns = [
    path('estadisticas/', views.estadisticas_productos_api, name='estadisticas_productos_api'), 
    path('', views.productos_api, name='productos_api'),
    path('<int:id>/', views.producto_detalle_api, name='producto_detalle_api'),
    path('categorias/', views.categorias_api, name='categorias_api'),
    path('categorias/<int:id>/', views.categoria_detalle_api, name='categoria_detalle_api'),
    
    
]
