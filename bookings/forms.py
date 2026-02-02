from django import forms
from .models import Booking
from datetime import date

class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date':   forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end   = cleaned_data.get('end_date')

        if not start or not end:
            return cleaned_data

        if start >= end:
            raise forms.ValidationError("Дата окончания должна быть позже начала")

        if start < date.today():
            raise forms.ValidationError("Нельзя бронировать прошедшие даты")

        # Проверка пересечения
        if self.product:
            overlapping = Booking.objects.filter(
                product=self.product,
                status__in=['confirmed', 'active'],
                start_date__lt=end,
                end_date__gt=start
            ).exists()

            if overlapping:
                raise forms.ValidationError("Эти даты уже заняты")

        return cleaned_data