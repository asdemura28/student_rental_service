from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from bookings.models import Booking


class Command(BaseCommand):
    help = 'Отправляет напоминания арендаторам о возврате товара за 1 день до окончания аренды'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)

        # Находим активные бронирования, которые заканчиваются завтра
        bookings_to_remind = Booking.objects.filter(
            status='active',
            end_date=tomorrow
        ).select_related('renter', 'product')

        reminded_count = 0

        for booking in bookings_to_remind:
            # Текст письма
            subject = f'Напоминание: возврат {booking.product.name} завтра'
            message = (
                f'Здравствуйте, {booking.renter.username}!\n\n'
                f'Напоминаем, что аренда товара "{booking.product.name}" заканчивается завтра — {booking.end_date}.\n'
                f'Пожалуйста, верните товар вовремя, чтобы избежать штрафов.\n\n'
                f'Если у вас возникли вопросы — свяжитесь с владельцем: {booking.product.owner.email}\n\n'
                f'С уважением,\n'
                f'Команда Student Rental Service'
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.renter.email],
                fail_silently=False,
            )

            reminded_count += 1
            self.stdout.write(self.style.SUCCESS(
                f'Напоминание отправлено арендатору {booking.renter.username} для товара "{booking.product.name}"'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Всего отправлено напоминаний: {reminded_count}'
        ))