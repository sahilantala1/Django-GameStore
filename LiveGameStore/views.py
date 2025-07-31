from django.db.models.fields import return_None
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Product,Cart,CartItem
from .forms import CreateUserForm,ProductForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.

def login_page(req):
    if req.user.is_authenticated:
        return redirect('home')
    else:
        if req.method == "POST":
            username = req.POST.get('username')
            password = req.POST.get('password')

            user = authenticate(req,username=username,password=password)
            if user is not None:
                login(req,user)
                return redirect('home')
            else:
                messages.info(req,'UserName Or Password is incorrect')
                return render(req,'login.html')

    context = {}
    return render(req,'login.html',context)

def logout_User(req):
    logout(req)
    return redirect('login')

def register(req):
    if req.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if req.method == 'POST':
            form = CreateUserForm(req.POST)
            if form.is_valid():
                form.save()
                return redirect('login')

        context = {'form':form}
        return render(req,'register.html',context)
#
# @login_required(login_url='login')
def home(req):
    context ={}
    return render(req,'index.html',context)

# @login_required(login_url='login')
def products(req):
    query = req.GET.get('q', '').strip()
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query)  # If category is a ForeignKey
        )
    context = {'products':products}
    return render(req,'products.html',context)

@login_required(login_url='login')
def adminviewpage(req):
    context={}
    return render(req,'admin_page.html',context)

@login_required(login_url='login')
def manageProduct(req):
    products = Product.objects.all()
    categories = Product.CATEGORY

    # Individual filters
    name_query = req.GET.get('name', '').strip()
    category_query = req.GET.get('category', '').strip()
    price_query = req.GET.get('price', '').strip()
    q = req.GET.get('q', '').strip()

    # Apply filters
    if name_query:
        products = products.filter(name__icontains=name_query)

    if category_query:
        products = products.filter(category__icontains=category_query)  # if category is a CharField

    if price_query:
        try:
            products = products.filter(price__lte=float(price_query))
        except ValueError:
            pass

    # General search box
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(category__icontains=q)
        )

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_query,
        'request': req
    }
    return render(req, 'manage_product.html', context)

@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_product')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def delete_product(req,id):
    if req.method == 'POST':
        product = get_object_or_404(Product, id=id)
        product.delete()
        return redirect('manage_product')

    return redirect('manage_product')

def edit_product(request ,id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)  # Important: include request.FILES!
        if form.is_valid():
            form.save()
            return redirect('manage_product')  # Or your product list URL name
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form
    }
    return render(request,'edit_product.html',context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('show_cart')

from django.shortcuts import render
from .models import Cart

def show_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        cart_items = []
        total = 0
    else:
        cart_items = cart.items.all()
        total = cart.total_price()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

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

def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('show_cart')

def product_detail(request,id):
    product_data = Product.objects.get(id=id)

    context = {'product_data':product_data}
    return render(request,'product_details.html',context)