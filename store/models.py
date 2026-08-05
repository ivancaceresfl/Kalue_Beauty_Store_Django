from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name        = 'Categoría'
        verbose_name_plural = 'Categorías'
        db_table            = 'category'

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name     = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )

    class Meta:
        verbose_name        = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        db_table            = 'subcategory'

    def __str__(self):
        return f'{self.category.name} → {self.name}'


class Product(models.Model):
    name                 = models.CharField(max_length=100)
    brand                = models.CharField(max_length=100)
    short_description    = models.CharField(max_length=200, blank=True)
    detailed_description = models.TextField(blank=True)
    subcategory          = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Producto'
        verbose_name_plural = 'Productos'
        db_table            = 'product'

    def __str__(self):
        return f'{self.name} — {self.brand}'

    @property
    def main_image(self):
        img = self.images.filter(main=True).first()
        return img.url_image if img else None

    @property
    def all_images(self):
        return list(self.images.values_list('url_image', flat=True))

    @property
    def active_variants(self):
        return self.variants.filter(active=True)

    @property
    def is_available(self):
        return any(v.is_available for v in self.active_variants)


class ProductImage(models.Model):
    product   = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    url_image = models.URLField()
    main      = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Imagen'
        verbose_name_plural = 'Imágenes'
        db_table            = 'productImage'

    def __str__(self):
        return f'Imagen de {self.product.name}'


class ProductVariant(models.Model):
    product         = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    color_or_number = models.CharField(max_length=50, blank=True)
    selling_price   = models.IntegerField()
    active          = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Variante'
        verbose_name_plural = 'Variantes'
        db_table            = 'productVariant'

    def __str__(self):
        return f'{self.product.name} — {self.color_or_number or "Sin variante"}'

    @property
    def current_stock(self):
        try:
            return self.stock.current_quantity
        except Stock.DoesNotExist:
            return 0

    @property
    def is_available(self):
        return self.current_stock > 0

    @property
    def is_low_stock(self):
        try:
            return self.stock.current_quantity <= self.stock.min_stock
        except Stock.DoesNotExist:
            return True


class Stock(models.Model):
    variant          = models.OneToOneField(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock'
    )
    current_quantity = models.IntegerField(default=0)
    min_stock        = models.IntegerField(default=3)

    class Meta:
        verbose_name        = 'Stock'
        verbose_name_plural = 'Stock'
        db_table            = 'stock'

    def __str__(self):
        return f'{self.variant} — {self.current_quantity} unidades'


class PurchaseLot(models.Model):
    variant        = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='lots'
    )
    purchase_price = models.IntegerField()
    amount_entered = models.IntegerField()
    date_of_entry  = models.DateField()
    notes          = models.CharField(max_length=200, blank=True)

    remaining_amount = models.IntegerField(default=0, editable=False)

    class Meta:
        verbose_name        = 'Lote de compra'
        verbose_name_plural = 'Lotes de compra'
        db_table            = 'purchaseLot'

    def __str__(self):
        return f'Lote #{self.id} — {self.variant}'

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None

        if es_nuevo:
            self.remaining_amount = self.amount_entered

        super().save(*args, **kwargs)

        if es_nuevo:
            stock, _ = Stock.objects.get_or_create(
                variant  = self.variant,
                defaults = {'current_quantity': 0, 'min_stock': 3}
            )

            stock_anterior         = stock.current_quantity
            stock.current_quantity += self.amount_entered
            stock.save()

            StockMovement.objects.create(
                variant        = self.variant,
                lot            = self,
                type           = 'entrada',
                quantity       = self.amount_entered,
                previous_stock = stock_anterior,
                new_stock      = stock.current_quantity,
                reason         = f'Lote #{self.pk} — {self.notes or "Entrada de mercadería"}'
            )

    @property
    def profit_per_unit(self):
        return self.variant.selling_price - self.purchase_price

    @property
    def units_sold(self):
        return self.amount_entered - self.remaining_amount

    @property
    def total_profit(self):
        return self.profit_per_unit * self.units_sold

class Sale(models.Model):
    admin      = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales'
    )
    total      = models.IntegerField()
    discount   = models.IntegerField(default=0)
    note       = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Venta'
        verbose_name_plural = 'Ventas'
        db_table            = 'sale'

    def __str__(self):
        return f'Venta #{self.id} — Bs.{self.total}'


class StockMovement(models.Model):

    MOVEMENT_TYPES = [
        ('entrada', 'Entrada'),
        ('venta',   'Venta'),
        ('ajuste',  'Ajuste'),
        ('vencido', 'Vencido'),
    ]

    variant        = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='movements'
    )
    lot            = models.ForeignKey(
        PurchaseLot,
        on_delete=models.CASCADE,
        related_name='movements'
    )
    sale           = models.ForeignKey(
        Sale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements'
    )
    type           = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity       = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock      = models.IntegerField()
    reason         = models.CharField(max_length=200, blank=True)
    admin          = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='movements'
    )
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Movimiento de stock'
        verbose_name_plural = 'Movimientos de stock'
        db_table            = 'stockMovement'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.type} — {self.variant} — {self.quantity} unidades'