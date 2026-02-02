from django.db import models
from django.conf import settings
from bookings.models import Booking

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('booking', 'reviewer')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем средний рейтинг арендодателя
        landlord = self.landlord
        reviews = landlord.received_reviews.all()
        if reviews.exists():
            landlord.rating = sum(r.rating for r in reviews) / reviews.count()
            landlord.rating_count = reviews.count()
        else:
            landlord.rating = 0.0
            landlord.rating_count = 0
        landlord.save()