# catalog/forms.py
from django import forms
from .models import Product, Category

class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'daily_price', 'weekly_price', 'deposit', 'photo', 'author']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'daily_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'weekly_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'deposit': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Выберите категорию"