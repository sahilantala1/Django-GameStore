from itertools import count
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.template import engines
from django.template.loader import render_to_string
from .models import Product, Cart, CartItem, Order
from .forms import *


def login_page(req):
    if req.user.is_authenticated:
        return redirect('home')

    if req.method == "POST":
        username = req.POST.get('username')
        password = req.POST.get('password')

        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            # You imported messages incorrectly, replace with Django messages framework if needed
            # For now, just render with context message
            context = {'error': 'Username or Password is incorrect'}
            return render(req, 'login.html', context)

    return render(req, 'login.html')


def logout_User(req):
    logout(req)
    return redirect('login')


def register(req):
    if req.user.is_authenticated:
        return redirect('home')

    form = CreateUserForm()
    if req.method == 'POST':
        form = CreateUserForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'form': form}
    return render(req, 'register.html', context)


# @login_required(login_url='login')
def home(req):
    context = {}
    return render(req, 'index.html', context)


def products(req):
    query = req.GET.get('q', '').strip()
    query_select = req.GET.getlist('qs')
    products = Product.objects.all()
    categories = Product.CATEGORY

    if query:
        products = products.filter(Q(name__icontains=query) | Q(category__icontains=query))

    if query_select:
        products = products.filter(category__in=query_select)

    pagination = Paginator(products, 8)
    page = req.GET.get('page')
    pageFinal = pagination.get_page(page)

    context = {
        'products': pageFinal,  # Paginated products
        'categories': categories,
        'selected_qs': query_select,
        'request': req,
        'pageFinal': pageFinal,
    }

    if req.headers.get('x-requested-with') == 'XMLHttpRequest':
        django_engine = engines['django']
        html_template = """
        {% for product in products %}
          <div class="col-sm-6 col-md-4 col-lg-3">
            <div class="product-card">
              <a href="{% url 'product_details' product.id %}">
                <img src="{{ product.image.url }}" alt="{{ product.name }}" class="product-img">
              </a>
              <div class="product-name">{{ product.name }}</div>
              <div class="product-price">${{ product.price }}</div>
              <div class="text-muted">Stock: {{ product.stock }}</div>
              {% if request.user.is_authenticated and not request.user.is_superuser %}
                <a href="{% url 'add_to_cart' product.id %}" class="btn btn-warning">Add to Cart</a>
              {% elif not request.user.is_authenticated %}
                <a href="{% url 'login' %}?next={% url 'add_to_cart' product.id %}" class="btn btn-warning">Add to Cart</a>
              {% endif %}
            </div>
          </div>
        {% empty %}
          <p class="text-center">No products available.</p>
        {% endfor %}
        """
        template = django_engine.from_string(html_template)
        html = template.render(context)
        return HttpResponse(html)

    return render(req, 'products.html', context)


@login_required(login_url='login')
def adminviewpage(req):
    context = {}
    return render(req, 'admin_page.html', context)


@login_required(login_url='login')
def manageProduct(request):
    products = Product.objects.all()
    categories = Product.CATEGORY  # [('Laptop', 'Laptop'), ('Monitor', 'Monitor'), ...]

    q = request.GET.get('q', '').strip()
    selected_qs = request.GET.getlist('qs')
    category_filter = request.GET.get('category')

    # Combine filters if applicable
    if q:
        products = products.filter(Q(name__icontains=q) | Q(category__icontains=q))

    if category_filter:
        selected_qs.append(category_filter)

    if selected_qs:
        products = products.filter(category__in=selected_qs)

    # Pagination after filtering
    paginator = Paginator(products, 5)
    page = request.GET.get('page')
    pageFinal = paginator.get_page(page)

    # AJAX response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        rows_html = render_to_string('product_rows.html', {'products': pageFinal.object_list})
        pagination_html = render_to_string('pagination.html', {'pageFinal': pageFinal, 'q': q})
        return JsonResponse({'rows_html': rows_html, 'pagination_html': pagination_html})

    context = {
        'products': pageFinal.object_list,
        'categories': categories,
        'pageFinal': pageFinal,
        'selected_qs': selected_qs,
    }

    return render(request, 'manage_product.html', context)


@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('add_product')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


def delete_product(request, id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('manage_product')
    return redirect('manage_product')

def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect('show_cart')


def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('show_cart')


def show_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart_items = []
        total = 0
    else:
        cart_items = cart.items.all()
        total = cart.total_price()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('show_cart')

def product_detail(request, id):
    product_data = get_object_or_404(Product, id=id)
    context = {'product_data': product_data}
    return render(request, 'product_details.html', context)

def manage_user(request):
    query = request.GET.get('q', '')  # get search input from URL
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )
    else:
        users = User.objects.all()

    print(query)

    context = {
        'users': users,
        'query': query,  # so the input field retains the value
    }

    return render(request, 'manage_user.html', context)

def update_user(request,id):
    current_user = User.objects.get(id = id)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        # You can add validations here
        current_user.username = username
        current_user.email = email
        current_user.save()

        return redirect('manage_user')  # Go back to user list

    context = {'current_user':current_user}
    return render(request,'user_edit.html',context)

def delete_user(request,id):
    if request.method == "POST":
        user = get_object_or_404(User, id=id)
        user.delete()
        return redirect('manage_user')
    return HttpResponseNotAllowed(['POST'])

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('show_cart')

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart or cart.items.count() == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('show_cart')

    for item in cart.items.all():
        product = item.product

        # Check if stock is sufficient
        if product.stock < item.quantity:
            messages.error(request, f"Not enough stock for {product.name}.")
            return redirect('show_cart')

        # Place order
        Order.objects.create(
            user=request.user,
            product=product,
            image=product.image,
            quantity=item.quantity,
            price=item.total_price(),
            email=request.user.email
        )

        # Reduce stock
        product.stock -= item.quantity
        product.save()

    # Clear the cart
    cart.items.all().delete()

    messages.success(request, "Order placed successfully.")
    return redirect('product')


@login_required
def manage_orders(request):
    all_orders = Order.objects.all().order_by('-date')  # Full list
    paginator = Paginator(all_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_rev = sum(order.price for order in all_orders)
    total_customer = all_orders.values('user_id').distinct().count()

    context = {
        'orders': page_obj.object_list,       # Paginated orders
        'page_obj': page_obj,
        'all_orders': all_orders,             # Full queryset for stats
        'total_rev': total_rev,
        'total_customer': total_customer
    }
    return render(request, 'order_show.html', context)

def ajax_user_search(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )
    else:
        users = User.objects.all()

    return render(request, 'user_table_rows.html', {'users': users})

def order_history_customer(req, id):
    try:
        user = User.objects.get(id=id)
        orders_history = Order.objects.filter(user=user).order_by('-id')  # adjust "user" field as per your model
        context = {'orders_history': orders_history}
        return render(req, 'order_history_customer.html', context)
    except User.DoesNotExist:
        return render(req, 'order_history_customer.html', {'error': 'User not found.'})

def user_profile(req,id):
    try:
        user = User.objects.get(id=id)
        context = {'user':user}
        return render(req, 'user_profile.html', context)
    except User.DoesNotExist:
        return render(req,'user_profile.html', {'error': 'User Not Found'})

def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_product')  # Redirect back to edit page to show message
    else:
        form = ProductForm(instance=product)

    context = {'form': form}
    return render(request, 'edit_product.html', context)

def edit_profile(request):
    user = request.user
    print(user)
    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=user)
        print("form.is_valid():", form.is_valid())
        print("Form errors:", form.errors)

        if form.is_valid():
            form.save()
            return redirect('user_profile',id=user.id)
    else:
        form = EditUserForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})