from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Cart, CartItem, Product, ProductInventory, Order, OrderItem, Category


# LIMPIEZA DE STOCK CADA 15 MINUTOS
def release_expired_stock():
    limit_time = timezone.now() - timedelta(minutes=15)
    expired_items = CartItem.objects.filter(created_at__lt=limit_time)

    for item in expired_items:
        if item.stock_item:
            item.stock_item.stock += item.quantity
            item.stock_item.save()
        item.delete()


def home(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all().order_by("name")

    categoria_slug = request.GET.get("categoria") or ""
    orden = request.GET.get("orden") or ""

    if categoria_slug:
        products = products.filter(category__slug=categoria_slug)

    if orden == "precio_asc":
        products = products.order_by("price")
    elif orden == "precio_desc":
        products = products.order_by("-price")

    context = {
        "products": products,
        "categories": categories,
        "categoria_actual": categoria_slug,
        "orden_actual": orden,
    }
    return render(request, "store/home.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "store/detail.html", {"product": product})


@login_required(login_url="accounts:login")
def cart_detail(request):
    release_expired_stock()
    cart = Cart.objects.filter(user=request.user).first()
    items = []
    total = 0
    expiry_timestamp = None

    if cart:
        items = list(cart.items.select_related("product", "stock_item").all())
        total = sum(item.total_price for item in items)
        if items:
            oldest_item_time = min(item.created_at for item in items)
            expires_at = oldest_item_time + timedelta(minutes=15)
            expiry_timestamp = int(expires_at.timestamp() * 1000)

    context = {
        "cart": cart,
        "items": items,
        "total": total,
        "expiry_timestamp": expiry_timestamp,
    }

    return render(request, "store/cart.html", context)


@login_required(login_url="accounts:login")
def add_to_cart(request, product_id):
    release_expired_stock()

    if request.method == "POST":
        inventory_id = request.POST.get("inventory_id")
        if not inventory_id:
            messages.error(request, "Seleccioná un talle")
            return redirect(
                "store:product_detail", slug=Product.objects.get(id=product_id).slug
            )

        inventory_item = get_object_or_404(ProductInventory, id=inventory_id)

        if inventory_item.stock <= 0:
            messages.error(request, "Sin stock")
            return redirect(
                "store:product_detail", slug=Product.objects.get(id=product_id).slug
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)

        CartItem.objects.create(
            cart=cart,
            product=inventory_item.product,
            stock_item=inventory_item,
            quantity=1,
        )

        inventory_item.stock -= 1
        inventory_item.save()

        return redirect("store:cart_detail")

    return redirect("store:product_detail", slug=Product.objects.get(id=product_id).slug)


@login_required(login_url="accounts:login")
def checkout(request):
    release_expired_stock()
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Tu carrito está vacío o expiró el tiempo de reserva.")
        return redirect("store:home")

    items = list(cart.items.select_related("product", "stock_item").all())
    total = sum(item.total_price for item in items)

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total=total,
            status=Order.Status.PENDING_TRANSFER,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                stock_item=item.stock_item,
                quantity=item.quantity,
                price=item.product.price,
            )

        # Vaciar carrito (los productos ya quedaron descontados del stock)
        cart.items.all().delete()

        return render(
            request,
            "store/checkout_success.html",
            {
                "order": order,
                "items": items,
                "alias": "gonzalo.corradi",
            },
        )

    return render(
        request,
        "store/checkout.html",
        {
            "cart": cart,
            "items": items,
            "total": total,
            "alias": "gonzalo.corradi",
        },
    )