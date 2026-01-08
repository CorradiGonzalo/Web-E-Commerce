from django.db import models

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