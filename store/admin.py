from django.contrib import admin
from .models import (Category, Subcategory, Product, ProductImage,
                     ProductVariant, Stock, PurchaseLot, Sale, StockMovement)

class ProductImageInline(admin.TabularInline):
    model   = ProductImage
    extra   = 1
    verbose_name        = 'Imagen'
    verbose_name_plural = 'Imágenes'

class ProductVariantInline(admin.TabularInline):
    model   = ProductVariant
    extra   = 1
    verbose_name        = 'Variante'
    verbose_name_plural = 'Variantes'

class StockInline(admin.StackedInline):
    model  = Stock
    extra  = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name']
    search_fields = ['name']

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'name', 'category']
    list_filter   = ['category']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ['name', 'brand', 'subcategory', 'active', 'is_available']
    list_filter    = ['active', 'subcategory__category']
    search_fields  = ['name', 'brand']
    list_editable  = ['active']
    inlines        = [ProductImageInline, ProductVariantInline]

    def is_available(self, obj):
        return obj.is_available
    is_available.boolean     = True
    is_available.short_description = 'Disponible'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display  = ['product', 'color_or_number', 'selling_price',
                     'active', 'current_stock', 'is_low_stock']
    list_filter   = ['active']
    search_fields = ['product__name', 'color_or_number']
    inlines       = [StockInline]

    def current_stock(self, obj):
        return obj.current_stock
    current_stock.short_description = 'Stock actual'

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean      = True
    is_low_stock.short_description = 'Stock bajo'

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display  = ['variant', 'current_quantity', 'min_stock']
    search_fields = ['variant__product__name']

@admin.register(PurchaseLot)
class PurchaseLotAdmin(admin.ModelAdmin):
    list_display  = ['id', 'variant', 'purchase_price', 'amount_entered',
                     'remaining', 'date_of_entry', 'profit_per_unit']
    list_filter   = ['date_of_entry']
    search_fields = ['variant__product__name']

    exclude = ['remaining_amount']

    def remaining(self, obj):
        return obj.remaining_amount
    remaining.short_description = 'Quedan'

    def profit_per_unit(self, obj):
        return f'Bs. {obj.profit_per_unit}'
    profit_per_unit.short_description = 'Ganancia/unidad'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display    = ['id', 'total', 'discount', 'note', 'created_at']
    readonly_fields = ['created_at']
    search_fields   = ['note']

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display    = ['variant', 'type', 'quantity', 'previous_stock',
                       'new_stock', 'admin', 'created_at']
    list_filter     = ['type', 'created_at']
    readonly_fields = ['created_at']
    search_fields   = ['variant__product__name']