from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    category = models.CharField(max_length=100, verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(verbose_name="Остаток на складе")

    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

class Expense(models.Model):
    description = models.CharField(max_length=255, verbose_name="Описание")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата расхода")

    def __str__(self):
        return self.description



    def __str__(self):
        return f"{self.name} - {self.amount}"