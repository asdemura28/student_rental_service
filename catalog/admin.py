# catalog/admin.py
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'daily_price', 'deposit', 'author', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description', 'author', 'owner__username')