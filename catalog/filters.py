# catalog/filters.py
import django_filters
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Категория')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Автор')
    price_min = django_filters.NumberFilter(field_name='daily_price', lookup_expr='gte', label='Цена от')
    price_max = django_filters.NumberFilter(field_name='daily_price', lookup_expr='lte', label='Цена до')

    class Meta:
        model = Product
        fields = ['name', 'category', 'author', 'price_min', 'price_max']