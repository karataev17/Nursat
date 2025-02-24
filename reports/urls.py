from django.urls import path, include
from rest_framework.routers import DefaultRouter


from django.urls import path
from .views import (
    dashboard,
     add_sale
)
from django.views.i18n import set_language
from django.urls import path
from .views import register_user, login_user
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import dashboard_view
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('sales/add/', add_sale, name='add_sale'),
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

    path('contacts/', views.contacts, name='contacts'),
]

from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.views.i18n import set_language

urlpatterns += [
    path('set-language/', set_language, name='set_language'),
]



from django.urls import path
from .views import analysis, add_sale, delete_sale

urlpatterns += [
    path('analysis/', analysis, name='analysis'),
    path('add_sale/', add_sale, name='add_sale'),
    path('delete_sale/<int:sale_id>/', delete_sale, name='delete_sale'),
]

from django.urls import path
from .views import statistics_view
urlpatterns += [
    path('statistics/', statistics_view, name='statistics'),
]




from django.urls import path
from .views import upload_excel

urlpatterns += [
    path("upload_excel/", upload_excel, name="upload_excel"),
]
from django.urls import path
from .views import report_view, save_report, delete_report, generate_report,export_report_to_excel

urlpatterns += [
    path("report/", report_view, name="report"),
    path("save-report/", save_report, name="save_report"),
    path("delete-report/<int:report_id>/", delete_report, name="delete_report"),
    path("generate-report/", generate_report, name="generate_report"),
    path("export-report/", export_report_to_excel, name="export_report"),

]
from django.urls import path
from .views import detailed_report

urlpatterns += [
    # Другие URL
    path('report/<str:product_type>/', detailed_report, name='detailed_report'),
]
from .views import export_detailed_report

from django.urls import path
from .views import detailed_report, export_detailed_report

urlpatterns += [
    path('report/<str:product_type>/', detailed_report, name='detailed_report'),
    path('export-report/<str:product_type>/', export_detailed_report, name='export_detailed_report'),
]


