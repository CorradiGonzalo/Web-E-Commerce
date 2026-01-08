from django.shortcuts import render, get_object_or_404
from .models import Product

def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, slug):
    #BUSCAMOS PRODUCTO POR URL
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/detail.html', {'product': product})