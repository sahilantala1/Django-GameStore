from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Product, Profile


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'category', 'image']

class ManageUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Add other editable fields here
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
