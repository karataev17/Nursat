
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


from django import forms
from .models import SaleRecord, Branch


class SaleRecordForm(forms.ModelForm):
    class Meta:
        model = SaleRecord
        fields = ['branch', 'product_type', 'name', 'quantity', 'retail_price', 'cost_price', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01'}),
            'product_type': forms.Select(choices=SaleRecord.PRODUCT_CHOICES),  # 👈 Теперь список выбора
        }
