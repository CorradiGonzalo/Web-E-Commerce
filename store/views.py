from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import Product, Cart, CartItem, ProductInventory

# LIMPIEZA DE STOCK CADA 15 MINUTOS
def release_expired_stock():
    limit_time = timezone.now() - timedelta(minutes=15)
    expired_items = CartItem.objects.filter(created_at__lt=limit_time)

    for item in expired_items:
        if item.stock_item:
            print(f"Devolviendo stock de: {item.product.name}")
            item.stock_item.stock += item.quantity
            item.stock_item.save()
        item.delete()

def home(request):
    release_expired_stock()
    products = Product.objects.filter(is_active=True)
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/detail.html', {'product': product})

def add_to_cart(request, product_id):
    release_expired_stock()

    if request.method == 'POST':
        # OBTENEMOS EL ID DEL INVENTARIO (TALLE) DESDE EL FORMULARIO
        inventory_id = request.POST.get('inventory_id')
        
        # BUSCAMOS STOCK ESPECIFICO
        inventory_item = get_object_or_404(ProductInventory, id=inventory_id)
        
        # VERIFICAMOS STOCK REAL
        if inventory_item.stock > 0:
            
            
            if request.user.is_authenticated:
                # CREAMOS (O RECUPERAMOS) EL CARRITO
                cart, created = Cart.objects.get_or_create(user=request.user)

                # CREAR EL ITEM EN EL CARRO
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=inventory_item.product,
                    stock_item=inventory_item, 
                    quantity=1
                )

                # DESCONTAR EL STOCK
                inventory_item.stock -= 1
                inventory_item.save()

                print(f"Exito! {inventory_item.product.name} reservado")

                return redirect('store:cart_detail')
            else:
                # Si no está logueado, lo mandamos al login
                return redirect('/admin/')
                
        else:
            print("Error: No hay stock")

    # Si falla algo, volvemos al detalle
    return redirect('store:product_detail', slug=Product.objects.get(id=product_id).slug)

def cart_detail(request):
    release_expired_stock() 
    cart = None
    items = []
    total = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            items = cart.items.select_related('product', 'stock_item').all()

            total = sum(item.total_price for item in items)
        
        context = {
            'cart': cart,
            'items': items,
            'total': total,
        }

        return render(request, 'store/cart.html', context)

def add_to_cart(request, product_id):
    print("Exito! {inventory_item.product.name} reservado")

    return redirect('store:cart_detail')
