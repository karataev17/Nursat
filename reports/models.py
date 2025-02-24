from django.db import models

class Branch(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название филиала")

    def __str__(self):
        return self.name


from django.db import models
from datetime import date

class SaleRecord(models.Model):
    PRODUCT_CHOICES = [
        ('beef', 'Говядина'),
        ('chicken', 'Курица'),
        ('lamb', 'Баранина'),
        ('horse', 'Конина'),
        ('other', 'Другое'),
    ]
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name="sales")
    product_type = models.CharField(max_length=20, choices=PRODUCT_CHOICES, default='other')
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    retail_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # Разрешаем NULL
    date = models.DateField()
    def save(self, *args, **kwargs):
        if self.retail_price and self.cost_price:
            self.net_profit = (self.retail_price - self.cost_price) * self.quantity  # Автоматически считаем прибыль
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.branch.name}"

from django.utils.timezone import now

from django.db import models
from django.utils.timezone import now


class ReportRecord(models.Model):
    name = models.CharField(max_length=255)
    sum = models.FloatField()
    date = models.DateField(default=now)  # ✅ Дата с дефолтным значением
    time = models.TimeField()

    def __str__(self):
        return f"{self.name} - {self.date} - {self.sum}"