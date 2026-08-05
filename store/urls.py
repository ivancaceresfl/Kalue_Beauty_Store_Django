from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
]