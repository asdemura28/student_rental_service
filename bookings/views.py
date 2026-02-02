from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from catalog.models import Product
from .models import Booking
from .forms import BookingCreateForm


@login_required
def create_booking(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if product.owner == request.user:
        messages.error(request, "Нельзя бронировать свой предмет")
        return redirect('catalog:product_detail', pk=product.pk)

    if request.method == 'POST':
        form = BookingCreateForm(request.POST, product=product)
        if form.is_valid():
            new_start = form.cleaned_data['start_date']
            new_end = form.cleaned_data['end_date']

            # Проверяем пересечение с подтверждёнными/активными бронями
            overlapping = product.booking_set.filter(
                status__in=['confirmed', 'active'],
                start_date__lte=new_end,           # начало старой брони ≤ конец новой
                end_date__gte=new_start            # конец старой ≥ начало новой
            ).exists()

            if overlapping:
                messages.error(request, 'Выбранные даты уже заняты. Выберите другие.')
                # Возвращаем форму с ошибкой, но сохраняем введённые даты
                context = {
                    'product': product,
                    'form': form,
                    'events': get_calendar_events(product),  # функция ниже
                }
                return render(request, 'bookings/create.html', context)

            # Если нет пересечения — сохраняем
            booking = form.save(commit=False)
            booking.renter = request.user
            booking.product = product

            days = (booking.end_date - booking.start_date).days
            booking.total_cost = product.daily_price * days
            booking.save()

            # Уведомление арендодателю
            send_mail(
                subject=f'Новый запрос на аренду: {product.name}',
                message=f'Пользователь {request.user.username} хочет арендовать "{product.name}"\n'
                        f'Даты: {booking.start_date} — {booking.end_date}\n'
                        f'Стоимость: {booking.total_cost} ₽\n\n'
                        f'Проверить: {request.build_absolute_uri(reverse("bookings:owner_requests"))}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[product.owner.email],
                fail_silently=False,
            )

            messages.success(request, "Запрос отправлен. Ожидайте подтверждения.")
            return redirect('bookings:my_bookings')

        else:
            messages.error(request, "Проверьте правильность заполнения формы.")
    else:
        form = BookingCreateForm(product=product)

    # Для GET-запроса или ошибки — показываем календарь
    context = {
        'product': product,
        'form': form,
        'events': get_calendar_events(product),  # ← функция ниже
    }
    return render(request, 'bookings/create.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(renter=request.user).order_by('-start_date')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def owner_requests(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')

        booking = get_object_or_404(Booking, id=booking_id, product__owner=request.user)

        if action == 'confirm':
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, f"Бронирование подтверждено: {booking.product.name}")

            # Уведомление арендатору
            send_mail(
                subject=f'Ваше бронирование подтверждено: {booking.product.name}',
                message=f'Владелец подтвердил аренду "{booking.product.name}"\n'
                        f'Даты: {booking.start_date} — {booking.end_date}\n'
                        f'Стоимость: {booking.total_cost} ₽\n\n'
                        f'Подробности: {request.build_absolute_uri(reverse("bookings:my_bookings"))}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.renter.email],
                fail_silently=False,
            )

        elif action == 'cancel':
            booking.status = 'cancelled'
            booking.save()
            messages.error(request, f"Бронирование отклонено: {booking.product.name}")

            # Уведомление арендатору
            send_mail(
                subject=f'Ваше бронирование отклонено: {booking.product.name}',
                message=f'К сожалению, владелец отклонил запрос на аренду "{booking.product.name}".',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.renter.email],
                fail_silently=False,
            )

        return redirect('bookings:owner_requests')

    # GET-запрос — показываем список
    bookings = Booking.objects.filter(product__owner=request.user).order_by('-created_at')
    return render(request, 'bookings/owner_requests.html', {'bookings': bookings})

def get_calendar_events(product):
    """Возвращает список событий для FullCalendar (занятые даты)"""
    bookings = product.booking_set.filter(status__in=['confirmed', 'active'])
    events = []
    for b in bookings:
        events.append({
            "title": "Забронировано",
            "start": b.start_date.isoformat(),
            "end": (b.end_date + timedelta(days=1)).isoformat(),  # +1 день, чтобы end_date был занят
            "color": "#dc3545",
            "allDay": True
        })
    return events

@login_required
def leave_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, renter=request.user, status='completed')
    
    if hasattr(booking, 'review'):
        messages.error(request, "Вы уже оставили отзыв.")
        return redirect('bookings:my_bookings')

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        
        Review.objects.create(
            booking=booking,
            reviewer=request.user,
            landlord=booking.product.owner,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Отзыв успешно оставлен!")
        return redirect('bookings:my_bookings')

    return render(request, 'reviews/leave_review.html', {'booking': booking})