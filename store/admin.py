from django.contrib import admin
from .models import Category, Product, Size, ProductInventory

class ProductInventoryInline(admin.TabularInline):
    model = ProductInventory
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInventoryInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Size)