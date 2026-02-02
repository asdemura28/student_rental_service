from django.db import models
from django.conf import settings
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)  # Категория: учебник, калькулятор и т.д.
    def __str__(self):
        return self.name  
    
class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    author = models.CharField(max_length=200, blank=True, null=True, verbose_name="Автор")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name