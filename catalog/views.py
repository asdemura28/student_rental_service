from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import timedelta
import django_filters

from .models import Product
from .forms import ProductCreateForm
from .filters import ProductFilter


# Фильтр (уже с автором)
class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact', label='Категория')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Автор')
    price_min = django_filters.NumberFilter(field_name='daily_price', lookup_expr='gte', label='Цена от')
    price_max = django_filters.NumberFilter(field_name='daily_price', lookup_expr='lte', label='Цена до')

    class Meta:
        model = Product
        fields = ['name', 'category', 'author', 'price_min', 'price_max']


# Список товаров с пагинацией (рекомендуемый классовый подход)
class ProductListView(ListView):
    model = Product
    template_name = 'catalog/list.html'
    context_object_name = 'products'
    paginate_by = 12  # ← 12 товаров на страницу (можно изменить)

    def get_queryset(self):
        # Только доступные товары
        queryset = Product.objects.filter(is_available=True).select_related('category', 'owner')
        # Применяем фильтр
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


# Функциональный вариант (если хочешь оставить функцию вместо класса)
def product_list(request):
    queryset = Product.objects.filter(is_available=True).select_related('category', 'owner')
    product_filter = ProductFilter(request.GET, queryset=queryset)
    
    # Пагинация
    paginator = Paginator(product_filter.qs, 12)  # 12 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'filter': product_filter,
        'page_obj': page_obj,  # ← передаём объект пагинации
        'products': page_obj,  # можно использовать и page_obj
    }
    return render(request, 'catalog/list.html', context)


# Детальная страница товара
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    bookings = product.booking_set.filter(
        status__in=['confirmed', 'active']
    ).select_related('renter')

    events = []
    for booking in bookings:
        end_date_exclusive = booking.end_date + timedelta(days=1)
        events.append({
            'title': 'Забронировано',
            'start': booking.start_date.isoformat(),
            'end': end_date_exclusive.isoformat(),
            'color': '#dc3545',
            'allDay': True,
            'classNames': ['fc-booked-event'],
        })

    context = {
        'product': product,
        'events_json': json.dumps(events, cls=DjangoJSONEncoder),
    }
    return render(request, 'catalog/detail.html', context)


# Создание товара
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, 'Предмет успешно добавлен в каталог!')
            return redirect('catalog:product_detail', pk=product.pk)
        else:
            messages.error(request, 'Проверьте правильность заполнения формы.')
    else:
        form = ProductCreateForm()

    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Добавить новый предмет',
        'button_text': 'Добавить',
    })

@login_required
def my_products(request):
    # Все товары текущего пользователя
    products = Product.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'catalog/my_products.html', {'products': products})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)  # только свои товары

    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлён!')
            return redirect('catalog:my_products')
    else:
        form = ProductCreateForm(instance=product)

    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Редактировать товар',
        'button_text': 'Сохранить изменения',
    })

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удалён!')
        return redirect('catalog:my_products')

    return render(request, 'catalog/product_confirm_delete.html', {'product': product})