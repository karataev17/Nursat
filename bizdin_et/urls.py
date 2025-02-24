from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),  # Подключаем API
]
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.contrib import admin

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),  # Маршрут для смены языка
]

urlpatterns += i18n_patterns(
    path('', include('reports.urls')),  # Основное приложение
)

