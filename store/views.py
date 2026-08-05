from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Product, Category

def index(request):
    productos  = Product.objects.filter(active=True).prefetch_related(
        'images', 'variants__stock'
    ).select_related('subcategory__category')

    categorias = Category.objects.prefetch_related(
        'subcategories'
    ).all()

    return render(request, 'index.html', {
        'productos':        productos,
        'categorias':       categorias,
        'whatsapp_number':  settings.WHATSAPP_NUMBER,
    })

def producto_detalle(request, pk):
    producto = get_object_or_404(
        Product.objects.prefetch_related(
            'images', 'variants__stock'
        ),
        pk=pk,
        active=True
    )

    return render(request, 'producto_detalle.html', {
        'producto':        producto,
        'variantes':       producto.active_variants,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    })