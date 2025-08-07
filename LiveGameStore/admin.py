from django.contrib import admin
from .models import Product

# Step 4.1: Create custom AdminSite class
class CustomAdminSite(admin.AdminSite):
    site_header = "My Custom Admin"
    site_title = "Admin Panel"
    index_title = "Welcome"

    def each_context(self, request):
        context = super().each_context(request)
        context['custom_css'] = 'css/custom_admin.css'
        return context

# Step 4.2: Instantiate your custom admin site
admin_site = CustomAdminSite(name='myadmin')

# Step 4.3: Register your models with your custom admin site
admin_site.register(Product)
