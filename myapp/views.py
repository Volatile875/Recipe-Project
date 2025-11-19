from django.shortcuts import render,redirect, get_object_or_404
from .models import Recepie, Order, OrderItem
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation

@login_required(login_url='/login/')
def lag(request):
    if request.method == 'POST':
        recepie_image = request.FILES.get('recepie_image')
        recepie_name = request.POST.get('recepie_name')
        recepie_description = request.POST.get('recepie_description')
        price_str = request.POST.get('price') or '199'
        try:
            price = Decimal(price_str)
        except (InvalidOperation, TypeError):
            price = Decimal('199')

        Recepie.objects.create(
            recepie_image=recepie_image,
            recepie_name=recepie_name,
            recepie_description=recepie_description,
            price=price,
        )
        return redirect('lag')  # use the named URL

    
    queryset = Recepie.objects.all()
    
    if request.GET.get('search'):
        queryset = queryset.filter(recepie_name__icontains= request.GET.get('search'))
    
    context = {'recepies': queryset}
    return render(request, 'lag.html', context)


@login_required(login_url='/login/')
def update_recepie(request, id):
    recepie = get_object_or_404(Recepie, id=id)

    if request.method == 'POST':
        recepie.recepie_name = request.POST.get('recepie_name', recepie.recepie_name)
        recepie.recepie_description = request.POST.get('recepie_description', recepie.recepie_description)

        price_str = request.POST.get('price')
        if price_str:
            try:
                recepie.price = Decimal(price_str)
            except (InvalidOperation, TypeError):
                pass

        # Only replace the image if a new one was uploaded
        new_image = request.FILES.get('recepie_image')
        if new_image:
            recepie.recepie_image = new_image

        recepie.save()
        return redirect('lag')

    context = {'recepie': recepie}
    return render(request, 'update_recepie.html', context)

@login_required(login_url='/login/')
def delete_recepie(request, id):
    recepie = get_object_or_404(Recepie, id=id)
    recepie.delete()
    return redirect('lag')


# --------- Simple session-based cart & ordering flow ---------

def _get_cart(request):
    """Return the cart dict from session, creating it if missing."""
    cart = request.session.get('cart', {})
    return cart


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


@login_required(login_url='/login/')
def add_to_cart(request, id):
    recepie = get_object_or_404(Recepie, id=id, is_available=True)

    cart = _get_cart(request)
    # store quantity as int; keys as string for JSON-serializable session
    key = str(recepie.id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)

    messages.success(request, f"{recepie.recepie_name} added to cart.")
    return redirect('lag')


@login_required(login_url='/login/')
def view_cart(request):
    cart = _get_cart(request)
    ids = cart.keys()
    recepies = Recepie.objects.filter(id__in=ids)

    items = []
    total = 0
    for r in recepies:
        qty = cart.get(str(r.id), 0)
        line_total = r.price * qty
        total += line_total
        items.append({
            'recepie': r,
            'quantity': qty,
            'line_total': line_total,
        })

    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'cart.html', context)


@login_required(login_url='/login/')
def remove_from_cart(request, id):
    cart = _get_cart(request)
    key = str(id)
    if key in cart:
        del cart[key]
        _save_cart(request, cart)
        messages.success(request, "Item removed from cart.")
    return redirect('view-cart')


@login_required(login_url='/login/')
def place_order(request):
    cart = _get_cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('lag')

    ids = cart.keys()
    recepies = Recepie.objects.filter(id__in=ids, is_available=True)

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(user=request.user, status='PENDING', total_amount=0)
        total = 0

        for r in recepies:
            qty = cart.get(str(r.id), 0)
            if qty <= 0:
                continue
            line_total = r.price * qty
            OrderItem.objects.create(
                order=order,
                recepie=r,
                quantity=qty,
                price=r.price,
            )
            total += line_total

        order.total_amount = total
        order.save()

        # Clear cart
        _save_cart(request, {})

        messages.success(request, f"Order #{order.id} placed successfully.")
        return redirect('order-list')

    # If GET, just show a confirmation page using the same cart view
    return redirect('view-cart')


@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password')
            return redirect('login_page')

        # If authentication succeeded, log the user in and redirect
        login(request, user)
        return redirect('lag')

    # For GET (and other methods) render the login form
    return render(request, 'login.html')

def register_view(request):
    # Handle POST: create a new user after validating fields
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Basic validation
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')

        # create_user hashes the password correctly
        User.objects.create_user(
            username=username,
            email=email or None,
            password=password,
            first_name=first_name or '',
            last_name=last_name or '',
        )

        messages.success(request, 'Account created. Please log in.')
        return redirect('/login/')

    # For GET (and any other methods) render the registration form
    return render(request, 'register.html')


def logout_page(request):
    logout(request)
    return redirect('/login/')