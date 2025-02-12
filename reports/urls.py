from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SaleViewSet, ExpenseViewSet
from .views import dashboard, product_list, sale_list, expense_list

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'expenses', ExpenseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('products/', product_list, name='product_list'),
    path('sales/', sale_list, name='sale_list'),
    path('expenses/', expense_list, name='expense_list'),
]
from django.urls import path
from .views import (
    dashboard, product_list, sale_list, expense_list,
    add_product, add_sale, add_expense
)
from django.views.i18n import set_language
from django.urls import path
from .views import register_user, login_user
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import dashboard_view
urlpatterns += [
    path('', dashboard, name='dashboard'),
    path('products/', product_list, name='product_list'),
    path('sales/', sale_list, name='sale_list'),
    path('expenses/', expense_list, name='expense_list'),

    path('products/add/', add_product, name='add_product'),
    path('sales/add/', add_sale, name='add_sale'),
    path('expenses/add/', add_expense, name='add_expense'),
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path("", dashboard_view, name="dashboard"),
    path('set-language/', set_language, name='set_language'),
]
from django.urls import path
from .views import analysis_view
from . import views
urlpatterns += [
    path('analysis/', analysis_view, name='analysis'),
    path('statistics/', views.statistics, name='statistics'),
    path('report/',views.report, name = 'report'),
    path('contacts/', views.contacts, name='contacts'),
]

from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.views.i18n import set_language

urlpatterns += [
    path('set-language/', set_language, name='set_language'),
]












