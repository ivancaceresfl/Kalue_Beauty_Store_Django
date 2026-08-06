from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/productos/', views.dashboard_productos, name='dashboard_productos'),
    path('dashboard/producto/agregar/', views.dashboard_agregar, name='dashboard_agregar'),
    path('dashboard/producto/editar/<int:pk>/', views.dashboard_editar, name='dashboard_editar'),
    path('dashboard/producto/eliminar/<int:pk>/', views.dashboard_eliminar, name='dashboard_eliminar'),
    path('dashboard/stock/', views.dashboard_stock, name='dashboard_stock'),
    path('dashboard/stock/lote/agregar/', views.dashboard_agregar_lote, name='dashboard_agregar_lote'),
    path('dashboard/historial/', views.dashboard_historial, name='dashboard_historial'),
    path('dashboard/producto/<int:pk>/variante/agregar/', views.dashboard_agregar_variante, name='dashboard_agregar_variante'),
    path('dashboard/ventas/', views.dashboard_ventas, name='dashboard_ventas'),
    path('dashboard/ventas/registrar/', views.dashboard_registrar_venta, name='dashboard_registrar_venta'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    
]