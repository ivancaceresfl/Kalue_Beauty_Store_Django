from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from .models import (Product, Category, Subcategory, ProductVariant,
                     ProductImage, Stock, PurchaseLot, StockMovement, Sale)
from django.contrib.auth import authenticate, login,  logout


def es_admin(user):
    return user.is_superuser

def es_vendedor_o_admin(user):
    return user.is_superuser or user.groups.filter(name='Vendedor').exists()

admin_required    = user_passes_test(es_admin,            login_url='/admin/login/')
vendedor_required = user_passes_test(es_vendedor_o_admin, login_url='/admin/login/')

def index(request):
    productos  = Product.objects.filter(active=True).prefetch_related(
        'images', 'variants__stock'
    ).select_related('subcategory__category')

    categorias = Category.objects.prefetch_related('subcategories').all()

    return render(request, 'index.html', {
        'productos':       productos,
        'categorias':      categorias,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    })

def producto_detalle(request, pk):
    producto = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants__stock'),
        pk=pk, active=True
    )
    return render(request, 'producto_detalle.html', {
        'producto':        producto,
        'variantes':       producto.active_variants,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    })


@vendedor_required
def dashboard(request):
    productos        = Product.objects.all()
    total_productos  = productos.count()
    total_activos    = productos.filter(active=True).count()
    total_agotados   = sum(1 for p in productos if not p.is_available)
    movimientos      = StockMovement.objects.select_related('variant__product', 'admin').order_by('-created_at')[:5]
    variantes        = ProductVariant.objects.prefetch_related('lots').all()

    ventas = Sale.objects.all()
    total_ingresos  = sum(v.total for v in ventas)
    total_descuentos = sum(v.discount for v in ventas)

    movimientos_venta = StockMovement.objects.filter(type='venta').select_related('lot')
    total_costos = sum(m.quantity * m.lot.purchase_price for m in movimientos_venta)

    ganancia_total = total_ingresos - total_costos


    return render(request, 'dashboard/index.html', {
        'total_productos': total_productos,
        'total_activos':   total_activos,
        'total_agotados':  total_agotados,
        'movimientos':     movimientos,
        'ganancia_total':  ganancia_total,
        'total_ingresos':   total_ingresos,
        'total_descuentos': total_descuentos,
        'total_costos':     total_costos,
    })

@vendedor_required
def dashboard_productos(request):
    productos = Product.objects.prefetch_related(
        'images', 'variants__stock'
    ).select_related('subcategory__category').all()
    return render(request, 'dashboard/productos.html', {
        'productos': productos,
    })

@admin_required
def dashboard_agregar(request):
    categorias   = Category.objects.prefetch_related('subcategories').all()
    subcategorias = Subcategory.objects.all()

    if request.method == 'POST':
        producto = Product.objects.create(
            name                 = request.POST['nombre'],
            brand                = request.POST['marca'],
            short_description    = request.POST['frase'],
            detailed_description = request.POST['descripcion'],
            subcategory_id       = request.POST['subcategoria'],
            active               = 'active' in request.POST
        )

        if request.POST.get('imagen_principal'):
            ProductImage.objects.create(
                product   = producto,
                url_image = request.POST['imagen_principal'],
                main      = True
            )

        fotos = request.POST.get('fotos_adicionales', '').split('\n')
        for foto in fotos:
            foto = foto.strip()
            if foto:
                ProductImage.objects.create(
                    product   = producto,
                    url_image = foto,
                    main      = False
                )

        if request.POST.get('precio'):
            ProductVariant.objects.create(
                product         = producto,
                color_or_number = request.POST.get('variante', ''),
                selling_price   = int(request.POST['precio']),
                active          = True
            )

        messages.success(request, f'✅ Producto "{producto.name}" agregado correctamente')
        return redirect('dashboard_productos')

    return render(request, 'dashboard/producto_form.html', {
        'categorias':   categorias,
        'subcategorias': subcategorias,
        'producto':     None,
    })

@admin_required
def dashboard_editar(request, pk):
    producto     = get_object_or_404(Product, pk=pk)
    categorias   = Category.objects.prefetch_related('subcategories').all()
    subcategorias = Subcategory.objects.all()

    if request.method == 'POST':
        producto.name                 = request.POST['nombre']
        producto.brand                = request.POST['marca']
        producto.short_description    = request.POST['frase']
        producto.detailed_description = request.POST['descripcion']
        producto.subcategory_id       = request.POST['subcategoria']
        producto.active               = 'active' in request.POST
        producto.save()
        messages.success(request, f'✅ Producto "{producto.name}" actualizado')
        return redirect('dashboard_productos')

    return render(request, 'dashboard/producto_form.html', {
        'categorias':    categorias,
        'subcategorias': subcategorias,
        'producto':      producto,
    })

@admin_required
def dashboard_eliminar(request, pk):
    producto = get_object_or_404(Product, pk=pk)
    nombre   = producto.name
    producto.delete()
    messages.success(request, f'🗑️ Producto "{nombre}" eliminado')
    return redirect('dashboard_productos')

@vendedor_required
def dashboard_stock(request):
    variantes = ProductVariant.objects.prefetch_related(
        'stock', 'lots'
    ).select_related('product').filter(active=True)
    return render(request, 'dashboard/stock.html', {
        'variantes': variantes,
    })

@admin_required
def dashboard_agregar_lote(request):
    variantes = ProductVariant.objects.select_related('product').filter(active=True)

    if request.method == 'POST':
        PurchaseLot.objects.create(
            variant_id     = request.POST['variante'],
            purchase_price = int(request.POST['precio_costo']),
            amount_entered = int(request.POST['cantidad']),
            remaining_amount = int(request.POST['cantidad']),
            date_of_entry  = request.POST['fecha'],
            notes          = request.POST.get('notas', '')
        )
        messages.success(request, '✅ Lote agregado y stock actualizado')
        return redirect('dashboard_stock')

    return render(request, 'dashboard/agregar_lote.html', {
        'variantes': variantes,
    })

@vendedor_required
def dashboard_historial(request):
    movimientos = StockMovement.objects.select_related(
        'variant__product', 'lot', 'admin'
    ).order_by('-created_at')
    return render(request, 'dashboard/historial.html', {
        'movimientos': movimientos,
    })

@admin_required
def dashboard_agregar_variante(request, pk):
    producto = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        color   = request.POST.get('color_or_number', '')
        precio  = int(request.POST['precio'])

        ProductVariant.objects.create(
            product         = producto,
            color_or_number = color,
            selling_price   = precio,
            active          = True
        )
        messages.success(request, f'✅ Variante "{color}" agregada a {producto.name}')
        return redirect('dashboard_editar', pk=producto.pk)

    return render(request, 'dashboard/agregar_variante.html', {
        'producto': producto,
    })

@vendedor_required
def dashboard_ventas(request):
    ventas = Sale.objects.select_related('admin').order_by('-created_at')

    ventas_con_datos = []
    total_compras = 0
    total_ventas  = 0
    total_ganancias = 0

    for venta in ventas:
        movimiento = StockMovement.objects.select_related(
            'lot', 'variant'
        ).filter(sale=venta, type='venta').first()

        precio_compra = 0
        precio_venta  = venta.total
        ganancia      = 0
    
        if movimiento:
            precio_compra = movimiento.lot.purchase_price * movimiento.quantity
            ganancia      = precio_venta - precio_compra

        ventas_con_datos.append({
            'venta':         venta,
            'precio_compra': precio_compra,
            'precio_venta':  precio_venta,
            'ganancia':      ganancia,
        })

    return render(request, 'dashboard/ventas.html', {
        'ventas': ventas_con_datos,
    })
@vendedor_required
def dashboard_registrar_venta(request):
    variantes = ProductVariant.objects.select_related('product').filter(
        active=True,
        stock__current_quantity__gt=0 
    )

    if request.method == 'POST':
        variante_id = int(request.POST['variante'])
        cantidad    = int(request.POST['cantidad'])
        descuento = int(request.POST.get('descuento', 0))
        nota        = request.POST.get('nota', '')

        variante = get_object_or_404(ProductVariant, pk=variante_id)
        stock    = variante.stock

        if cantidad > stock.current_quantity:
            messages.error(request, f'❌ Stock insuficiente. Solo hay {stock.current_quantity} unidades.')
            return redirect('dashboard_registrar_venta')

        lote = variante.lots.filter(remaining_amount__gt=0).order_by('date_of_entry').first()

        if not lote:
            messages.error(request, '❌ No hay lotes disponibles para esta variante.')
            return redirect('dashboard_registrar_venta')

        stock_anterior = stock.current_quantity

        stock.current_quantity -= cantidad
        stock.save()

        lote.remaining_amount -= cantidad
        lote.save()

        total   = (variante.selling_price * cantidad) - descuento
        venta = Sale.objects.create(
            admin    = request.user,
            total    = total,
            discount = descuento,
            note     = nota
        )

        StockMovement.objects.create(
            variant        = variante,
            lot            = lote,
            sale           = venta,
            type           = 'venta',
            quantity       = cantidad,
            previous_stock = stock_anterior,
            new_stock      = stock.current_quantity,
            reason         = f'Venta #{venta.id} — {nota}'
        )

        messages.success(request, f'✅ Venta registrada — {cantidad} x {variante.product.name} '
                                  f'({variante.color_or_number}) — '
                                  f'{"Descuento: Bs." + str(descuento) + " — " if descuento else ""}'
                                  f'Total: Bs. {total}')

        return redirect('dashboard_ventas')

    return render(request, 'dashboard/registrar_venta.html', {
        'variantes': variantes,
    })

def es_admin(user):
    return user.is_superuser

def es_vendedor_o_admin(user):
    return user.is_superuser or user.groups.filter(name='Vendedor').exists()

def dashboard_login(request):
    if request.user.is_authenticated and es_vendedor_o_admin(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user     = authenticate(request, username=username, password=password)

        if user and es_vendedor_o_admin(user):
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')

    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    logout(request)
    return redirect('dashboard_login')

admin_required    = user_passes_test(es_admin,            login_url='/dashboard/login/')
vendedor_required = user_passes_test(es_vendedor_o_admin, login_url='/dashboard/login/')