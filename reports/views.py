from rest_framework import viewsets
from .models import Product, Sale, Expense
from .serializers import ProductSerializer, SaleSerializer, ExpenseSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
from django.shortcuts import render
from .models import Product, Sale, Expense

def dashboard(request):
    total_sales = Sale.objects.count()
    total_expenses = Expense.objects.count()
    total_products = Product.objects.count()

    context = {
        'total_sales': total_sales,
        'total_expenses': total_expenses,
        'total_products': total_products,
    }
    return render(request, 'reports/dashboard.html', context)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'reports/product_list.html', {'products': products})
def sale_list(request):
    sales = Sale.objects.all()
    return render(request, 'reports/sale_list.html', {'sales': sales})
def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'reports/expense_list.html', {'expenses': expenses})
from django.shortcuts import render, redirect
from .models import Product, Sale, Expense
from .forms import ProductForm, SaleForm, ExpenseForm

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'reports/add_product.html', {'form': form})
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm()
    return render(request, 'reports/add_sale.html', {'form': form})
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'reports/add_expense.html', {'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from .forms import RegisterForm

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Добавляем пользователя в группу "Менеджеры"
            managers_group, created = Group.objects.get_or_create(name='Менеджеры')
            user.groups.add(managers_group)
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'reports/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.groups.filter(name="Менеджеры").exists():  # Только менеджеры могут входить
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'reports/login.html', {'error': 'Доступ запрещен'})
    return render(request, 'reports/login.html')
from django.contrib.auth.decorators import login_required, user_passes_test

def is_manager(user):
    return user.groups.filter(name='Менеджеры').exists()

@login_required
@user_passes_test(is_manager)
def dashboard(request):
    return render(request, 'reports/dashboard.html')

from django.shortcuts import render

def dashboard_view(request):
    return render(request, "reports/dashboard.html")
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")  # Перенаправление на страницу входа после выхода
    return render(request, "accounts/logout.html")

def analysis_view(request):
    return render(request, 'analysis.html')

def statistics(request):
    return render(request, 'statistics.html')

def report(request):
    return render(request, "report.html")
from django.shortcuts import render

def contacts(request):
    return render(request, 'contacts.html')
