from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Главная страница каталога (/)
    path('', views.ProductListView.as_view(), name='product_list'),        
    # Детальная страница товара
    path('<int:pk>/', views.product_detail, name='product_detail'),
    # Добавление нового товара
    path('add/', views.product_create, name='product_create'),
    path('my-products/', views.my_products, name='my_products'),
    path('<int:pk>/update/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
]