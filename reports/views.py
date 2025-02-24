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


from django.db.models import Sum
from datetime import datetime, timedelta
from django.shortcuts import render
from .models import SaleRecord, Branch
from decimal import Decimal
# Средний вес туши для каждого вида мяса
AVERAGE_CARCASS_WEIGHT = {
    "beef": 250,      # Средний вес туши говядины ~250 кг
    "lamb": 20,       # Средний вес туши баранины ~20 кг
    "horse": 280,     # Средний вес туши конины ~280 кг
    "chicken": 2.5    # Средний вес курицы ~2.5 кг
}

def dashboard(request):
    today = datetime.today().date()
    one_month_ago = today - timedelta(days=30)

    branches = Branch.objects.all()
    selected_branch_id = request.GET.get('branch', None)

    sales_query = SaleRecord.objects.filter(date__range=[one_month_ago, today])

    if selected_branch_id:
        sales_query = sales_query.filter(branch_id=selected_branch_id)

    total_inventory = sales_query.aggregate(total_kg=Sum('quantity'))['total_kg'] or 0
    total_turnover = sales_query.aggregate(total_turnover=Sum('retail_price'))['total_turnover'] or 0
    total_expenses = sales_query.aggregate(total_expenses=Sum('cost_price'))['total_expenses'] or 0
    total_profit = total_turnover - total_expenses

    total_carcasses = Decimal(0)
    carcass_count_by_type = {}

    for product_type, avg_weight in AVERAGE_CARCASS_WEIGHT.items():
        total_weight = sales_query.filter(product_type=product_type).aggregate(Sum("quantity"))["quantity__sum"] or Decimal(0)
        carcass_count = total_weight / Decimal(avg_weight)  # Приводим `avg_weight` к Decimal
        carcass_count_by_type[product_type] = round(float(carcass_count), 2)  # Конвертируем обратно в `float`
        total_carcasses += carcass_count  # Теперь `Decimal` + `Decimal`

    context = {
        'branches': branches,
        'selected_branch_id': int(selected_branch_id) if selected_branch_id else None,
        'total_inventory': total_inventory,
        'total_turnover': total_turnover,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'total_carcasses': round(float(total_carcasses), 2),  # Конвертируем в `float` перед выводом
        'carcass_count_by_type': carcass_count_by_type,  # Список туш по видам
        'report_start_date': one_month_ago,
        'report_end_date': today,
    }
    return render(request, 'dashboard.html', context)




from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.http import HttpResponse
from .models import SaleRecord
PRODUCT_MAPPING = {
    "Говядина": "beef",
    "Конина": "horse",
    "Баранина": "lamb",
    "Курица": "chicken",
    "Другое": "other"
}
import pandas as pd
from datetime import datetime
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import SaleRecord, Branch

# Маппинг видов продукта на английский
PRODUCT_MAPPING = {
    "Говядина": "beef",
    "Курица": "chicken",
    "Баранина": "lamb",
    "Конина": "horse"
}

def upload_excel(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        excel_file = request.FILES["excel_file"]
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)

        try:
            df = pd.read_excel(file_path)

            # ✅ Убираем лишние пробелы в заголовках
            df.columns = df.columns.str.strip()

            # ✅ Проверяем, есть ли все нужные столбцы
            required_columns = {"Филиал", "Вид продукта", "Наименование", "Количество",
                                "Розничная сумма", "Себестоимость", "Чистая прибыль", "Дата"}
            missing_columns = required_columns - set(df.columns)

            if missing_columns:
                return HttpResponse(f"Ошибка: Отсутствуют столбцы {', '.join(missing_columns)}", status=400)

            # ✅ Чистим столбец "Вид продукта" от пробелов
            df["Вид продукта"] = df["Вид продукта"].astype(str).str.strip()

            # ✅ Разбираем список, если указано несколько значений (например, "Говядина, Конина")
            df["Вид продукта"] = df["Вид продукта"].apply(lambda x: x.split(",")[0] if "," in x else x)

            # ✅ Переводим вид продукта в английский
            df["Вид продукта"] = df["Вид продукта"].map(PRODUCT_MAPPING)

            # ✅ Если значение не найдено в PRODUCT_MAPPING, ставим "other"
            df["Вид продукта"].fillna("other", inplace=True)

            # ✅ Преобразуем дату в нужный формат
            df["Дата"] = pd.to_datetime(df["Дата"], format="%d.%m.%Y", errors="coerce")

            # ✅ Если дата не распозналась, ставим сегодняшнюю
            df["Дата"].fillna(datetime.now(), inplace=True)

            # ✅ Загружаем данные в базу
            for _, row in df.iterrows():
                branch_name = row["Филиал"].strip()
                try:
                    branch = Branch.objects.get(name=branch_name)
                except Branch.DoesNotExist:
                    messages.warning(request, f"Филиал '{branch_name}' не найден. Пропуск строки.")
                    continue

                SaleRecord.objects.create(
                    branch=branch,
                    name=row["Наименование"],
                    quantity=row["Количество"],
                    retail_price=row["Розничная сумма"],
                    cost_price=row["Себестоимость"],
                    net_profit=row["Чистая прибыль"],
                    date=row["Дата"],  # ✅ Теперь дата загружается правильно
                    product_type=row["Вид продукта"]  # ✅ Вид продукта сохраняется корректно
                )

            messages.success(request, "Данные успешно загружены!")
        except Exception as e:
            messages.error(request, f"Ошибка загрузки: {e}")

        return redirect("analysis")
    else:
        messages.error(request, "Файл не был выбран.")
        return redirect("analysis")

from django.shortcuts import render
from django.db.models import Sum

def dashboard_view(request):
    # Получаем общий вес каждого типа мяса
    total_weight = {
        "beef": SaleRecord.objects.filter(product_type="Говядина").aggregate(total_weight=Sum("quantity"))["total_weight"] or 0,
        "lamb": SaleRecord.objects.filter(product_type="Баранина").aggregate(total_weight=Sum("quantity"))["total_weight"] or 0,
        "horse": SaleRecord.objects.filter(product_type="Конина").aggregate(total_weight=Sum("quantity"))["total_weight"] or 0,
        "chicken": SaleRecord.objects.filter(product_type="Курица").aggregate(total_weight=Sum("quantity"))["total_weight"] or 0,
    }

    # Средний вес туши для каждого вида мяса
    average_weight = {
        "beef": 250,
        "lamb": 25,
        "horse": 300,
        "chicken": 2.5,
    }

    # Вычисляем общее количество туш
    total_carcasses = sum(total_weight[ptype] / average_weight[ptype] for ptype in total_weight if total_weight[ptype] > 0)

    context = {
        "total_inventory": sum(total_weight.values()),  # Общий вес в кг
        "total_carcasses": round(total_carcasses, 1),  # Количество туш (округление)
    }

    return render(request, "dashboard.html", context)
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")  # Перенаправление на страницу входа после выхода
    return render(request, "accounts/logout.html")

def analysis_view(request):
    branches = Branch.objects.all()
    selected_branch_id = request.GET.get('branch', branches.first().id if branches else None)
    sales = SaleRecord.objects.filter(branch_id=selected_branch_id) if selected_branch_id else []
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    sales = paginator.get_page(page_number)
    return render(request, 'analysis.html', {
        'branches': branches,
        'sales': sales,
        'selected_branch_id': int(selected_branch_id) if selected_branch_id else None,
    })
def statistics_view(request):
    logger.info("🔥 Функция statistics_view() вызвана!")


    branches = Branch.objects.all()

    if not branches.exists():
        logger.warning("❌ В базе нет филиалов!")
    else:
        logger.info(f"📌 Найденные филиалы: {list(branches.values_list('id', 'name'))}")

    print("Филиалы загружены:", list(branches.values_list('id', 'name')))  # Вывод в консоль

    selected_branch_id = request.GET.get('branch', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    sales_query = SaleRecord.objects.all()



    if selected_branch_id:
        sales_query = sales_query.filter(branch_id=selected_branch_id)

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            sales_query = sales_query.filter(date__range=[start_date, end_date])
        except ValueError:
            logger.error("❌ Ошибка: неверный формат даты!")

    # 📊 Группируем продажи по датам
    sales_data = sales_query.values('date').annotate(total_sales=Sum('quantity')).order_by('date')

    # Ограничиваем историю заказов до **7 последних записей**
    order_history = sales_query.values('id', 'date').order_by('-date')[:7]



    # 🔥 Рассчитываем общую статистику
    total_sales = sales_query.aggregate(total_sales=Sum('quantity'))['total_sales'] or 0
    total_revenue = sales_query.aggregate(total_revenue=Sum('retail_price'))['total_revenue'] or 0
    total_expenses = sales_query.aggregate(total_expenses=Sum('cost_price'))['total_expenses'] or 0
    total_profit = total_revenue - total_expenses

    # 🟢 ПЕРЕДАЧА ДАННЫХ В ШАБЛОН
    context = {
        'branches': branches,  # ✅ Филиалы
        'sales_data': sales_data,  # ✅ Продажи по датам
        'order_history': order_history,  # ✅ История заказов
        'selected_branch_id': selected_branch_id,  # ✅ Выбранный филиал
        'total_sales': total_sales,  # ✅ Количество продаж
        'total_revenue': total_revenue,  # ✅ Общий доход
        'total_expenses': total_expenses,  # ✅ Общие расходы
        'total_profit': total_profit,  # ✅ Чистая прибыль
    }

    return render(request, 'statistics.html', context)


def statistics(request):
    return render(request, 'statistics.html')

def report(request):
    return render(request, "report.html")
from django.shortcuts import render

def contacts(request):
    return render(request, 'contacts.html')


from .forms import SaleRecordForm

from django.core.paginator import Paginator
def analysis(request):
    branches = Branch.objects.all()
    selected_branch = request.GET.get('branch', None)
    sales_query = SaleRecord.objects.all().order_by('-date')
    if selected_branch:
        sales = SaleRecord.objects.filter(branch__id=selected_branch)
    else:
        sales = SaleRecord.objects.all()

    form = SaleRecordForm()
    paginator = Paginator(sales.order_by('-date'), 10)  # Сортируем по дате перед пагинацией

    page_number = request.GET.get('page')
    sales = paginator.get_page(page_number)
    return render(request, 'analysis.html', {
        'branches': branches,
        'sales': sales,
        'form': form,
        'selected_branch': selected_branch,
    })


def add_sale(request):
    if request.method == "POST":
        form = SaleRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('analysis')
    return redirect('analysis')


from django.urls import reverse

def delete_sale(request, sale_id):
    sale = get_object_or_404(SaleRecord, id=sale_id)
    branch_id = request.POST.get("branch", None)  # Получаем ID текущего филиала

    sale.delete()

    # Перенаправляем обратно на текущий филиал
    if branch_id:
        return redirect(f"{reverse('analysis')}?branch={branch_id}")
    return redirect("analysis")




import logging
logger = logging.getLogger(__name__)
# Настроим логирование в файл
logging.basicConfig(filename="debug.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")

from .models import SaleRecord, Branch




from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Sum

from datetime import datetime, timedelta


def report_view(request):
    reports = ReportRecord.objects.all().order_by('-date')  # Загружаем отчеты, сортируем по дате
    print("🔥 Загруженные отчёты:", list(reports.values()))
    return render(request, 'report.html', {"reports": reports})


import json
from datetime import datetime
from django.http import JsonResponse
from .models import ReportRecord

import json
from datetime import datetime
from django.http import JsonResponse
from .models import ReportRecord

def save_report(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            saved_reports = []

            for report in data["reports"]:
                try:
                    time_obj = datetime.strptime(report["time"], "%H:%M").time()
                    date_obj = datetime.strptime(report["date"], "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"error": "Некорректный формат даты или времени"}, status=400)

                new_report = ReportRecord.objects.create(
                    name=report["name"],
                    sum=float(report["sum"].replace(" ", "").replace(",", ".")),
                    date=date_obj,
                    time=time_obj
                )

                saved_reports.append({
                    "id": new_report.id,
                    "name": new_report.name,
                    "sum": new_report.sum,
                    "date": new_report.date.strftime("%Y-%m-%d"),
                    "time": new_report.time.strftime("%H:%M")
                })

            return JsonResponse({"message": "Отчет сохранен!", "saved_reports": saved_reports})

        except Exception as e:
            print("Ошибка при сохранении:", e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Метод не поддерживается"}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ReportRecord


def delete_report(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(ReportRecord, id=report_id)
        report.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Неверный запрос"}, status=400)
def generate_report(request):
    reports = ReportRecord.objects.all()
    return render(request, "generated_report.html", {"reports": reports})

from django.http import HttpResponse
import pandas as pd
from datetime import datetime
def export_report_to_excel(request):
    reports = ReportRecord.objects.all().values("name", "sum", "time", "date")

    df = pd.DataFrame(list(reports.values()))

    # Убираем временную зону у всех datetime полей
    for column in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
        df[column] = df[column].apply(lambda x: x.replace(tzinfo=None) if pd.notnull(x) else x)
    df.rename(columns={"name": "Наименование", "sum": "Сумма", "time": "Время", "date": "Дата"}, inplace=True)

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="Отчет.xlsx"'
    df.to_excel(response, index=False)

    return response
from django.shortcuts import render
from .models import ReportRecord

def report_view(request):
    search_query = request.GET.get('search', '').strip()
    reports = ReportRecord.objects.all()

    if search_query:
        reports = reports.filter(name__icontains=search_query)

    return render(request, 'report.html', {'reports': reports})

from django.shortcuts import render
from django.core.paginator import Paginator
from .models import SaleRecord


from django.core.paginator import Paginator
from django.shortcuts import render
from .models import SaleRecord

def detailed_report(request, product_type):
    product_names = {
        "horse": "Конина",
        "beef": "Говядина",
        "lamb": "Баранина",
        "chicken": "Курица"
    }

    if product_type not in product_names:
        return render(request, "404.html")

    sales = SaleRecord.objects.filter(product_type=product_type).select_related("branch").order_by('-date')

    # Пагинация: 10 записей на страницу
    paginator = Paginator(sales, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "detailed_report.html", {
        "sales": page_obj,
        "product_name": product_names[product_type],
        "product_type": product_type
    })


import pandas as pd
from django.http import HttpResponse
from .models import SaleRecord

def export_detailed_report(request, product_type):
    product_names = {
        "horse": "Конина",
        "beef": "Говядина",
        "lamb": "Баранина",
        "chicken": "Курица"
    }

    if product_type not in product_names:
        return HttpResponse("Ошибка: Неверный тип продукта", status=400)

    sales = SaleRecord.objects.filter(product_type=product_type).select_related("branch")

    df = pd.DataFrame.from_records(sales.values("branch__name", "name", "quantity", "retail_price", "cost_price", "net_profit", "date"))

    # Преобразуем date в формат datetime (чтобы избежать ошибки)
    df["date"] = pd.to_datetime(df["date"], errors='coerce')

    # Убираем таймзону (если есть)
    df["date"] = df["date"].dt.tz_localize(None)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{product_names[product_type]}_report.xlsx"'
    df.to_excel(response, index=False)

    return response

