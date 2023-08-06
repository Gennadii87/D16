import os
from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils import timezone

# Автор объявления
class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.authorUser.username}"
# Товар для нашей витрины
class Product(models.Model):
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    icon = RichTextField(
        verbose_name='Иконка',
        blank=True,  # поле необязательное, может быть пустым
    )
    name = models.TextField(
        max_length=254,
        unique=True, # названия товаров не должны повторяться
        verbose_name='Название',
    )
    description = RichTextField(verbose_name = 'Описание')
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], verbose_name = 'Количество'
    )
    # поле категории будет ссылаться на модель категории
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='products', # все продукты в категории будут доступны через поле products
        verbose_name='Категория',
    )
    price = models.FloatField(
        validators=[MinValueValidator(0.0)],
        verbose_name = 'Цена',
    )
    created_at = models.DateTimeField(
        #auto_now_add=True,  # Заполнение текущей датой и временем при создании нового объекта
        default=timezone.now,  # Значение по умолчанию - текущая дата и время
        verbose_name='Дата создания',
    )
    def __str__(self):
        return f"{self.name.title()}:\nКатегория: {self.category}\nЦена: {self.price}"

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.id)])


# Категория, к которой будет привязываться товар
class Category(models.Model):
    TANKS = 'Танки'
    HEALERS = 'Хилы'
    DPS = 'ДД'
    TRADERS = 'Торговцы'
    GUILD_MASTERS = 'Гилдмастеры'
    QUEST_GIVERS = 'Квестгиверы'
    BLACKSMITHS = 'Кузнецы'
    LEATHERWORKERS = 'Кожевники'
    ALCHEMISTS = 'Зельевары'
    SPELL_MASTERS = 'Мастера заклинаний'

    CATEGORY_CHOICES = [
        (TANKS, 'Танки'),
        (HEALERS, 'Хилы'),
        (DPS, 'ДД'),
        (TRADERS, 'Торговцы'),
        (GUILD_MASTERS, 'Гилдмастеры'),
        (QUEST_GIVERS, 'Квестгиверы'),
        (BLACKSMITHS, 'Кузнецы'),
        (LEATHERWORKERS, 'Кожевники'),
        (ALCHEMISTS, 'Зельевары'),
        (SPELL_MASTERS, 'Мастера заклинаний'),
    ]

    name = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name.title()


class Subscription(models.Model):

    class Meta:

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    user = models.ForeignKey(
                to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь',
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Категория',
    )
    def __str__(self):
        return f'Список'

class Comment(models.Model):

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользователь',
    )
    product = models.ForeignKey(
        to='Product',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Продукт',
    )
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    accepted = models.BooleanField(default=False, verbose_name='Принят', choices=[(False, 'Не принят'), (True, 'Принят')])

    def __str__(self):
        return f'Автор: {self.user.username}, Продукт: {self.product.name}'