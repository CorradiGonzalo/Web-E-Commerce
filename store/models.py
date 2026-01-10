from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    slug = models.SlugField(unique=True) 

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Talle") 
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Categoría")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagen")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductInventory(models.Model):
    product = models.ForeignKey(Product, related_name='inventory', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Talle")
    stock = models.PositiveIntegerField(default=0, verbose_name="Cantidad")

    class Meta:
        unique_together = ('product', 'size')
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

    def __str__(self):
        return f"{self.product.name} ({self.size.name})"
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updeted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_item = models.ForeignKey(ProductInventory, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.stock_item.size.name})"
    
        @property
        def total_proce(self):
            return self.quantity * self.product.price
        