from django import forms
from .models import Product, Sale, Expense

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'total_price']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount']
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'placeholder': 'Введите свой адрес электронной почты'
    }))
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput(attrs={
        'placeholder': 'Введите свое имя пользователя'
    }))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите свой пароль'
    }))
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput(attrs={
        'placeholder': 'Повторите свой пароль'
    }))

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']
