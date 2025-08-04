from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('home/', views.home,name='home'),
    path('products/',views.products,name="product"),
    path('login/',views.login_page,name="login"),
    path('admin_login/',views.adminviewpage,name="admin_login"),
    path('logout/',views.logout_User,name="logout"),
    path('register/',views.register,name="register"),
    path('manage_product/',views.manageProduct,name="manage_product"),
    path('add_product/',views.add_product,name="add_product"),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.show_cart, name='show_cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('product_details/<int:id>', views.product_detail, name='product_details'),
    path('manage_user/', views.manage_user, name='manage_user'),
    path('user_edit/<int:id>', views.update_user, name='user_edit'),
    path('delete_user/<int:id>', views.delete_user, name='delete_user'),
]