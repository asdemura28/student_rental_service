from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомная модель пользователя с дополнительными полями для сервиса аренды.
    """

    # Дополнительные поля
    university = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Университет")
    )
    student_id_photo = models.ImageField(
        upload_to='student_ids/',
        blank=True,
        null=True,
        verbose_name=_("Фото студенческого билета")
    )
    rating = models.FloatField(
        default=0.0,
        verbose_name=_("Средний рейтинг")
    )
    rating_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Количество оценок")
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Верифицирован")
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Номер телефона")
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_("О себе")
    )

    # Исправляем конфликты related_name для групп и разрешений
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',           # ← уникальное имя
        blank=True,
        help_text=_('Группы, в которых состоит пользователь.'),
        verbose_name=_('группы'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # ← уникальное имя
        blank=True,
        help_text=_('Конкретные разрешения пользователя.'),
        verbose_name=_('разрешения пользователя'),
    )

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def average_rating(self):
        """Удобное свойство для вывода рейтинга (округляем до 1 знака)"""
        return round(self.rating, 1) if self.rating_count > 0 else 0.0

    def update_rating(self):
        """Обновляет средний рейтинг на основе всех полученных отзывов"""
        from reviews.models import Review  # Импорт внутри метода, чтобы избежать циклического импорта

        reviews = Review.objects.filter(landlord=self)
        count = reviews.count()

        if count > 0:
            total = sum(review.rating for review in reviews)
            self.rating = total / count
            self.rating_count = count
        else:
            self.rating = 0.0
            self.rating_count = 0

        self.save(update_fields=['rating', 'rating_count'])