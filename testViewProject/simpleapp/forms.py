from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from .models import *


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'icon', 'name', 'description', 'category', 'price', 'quantity', ]

        labels = {
            'icon': 'Иконка',
            'name': 'Наименование',
            'description': 'Описание',
            'category': 'Категория',
            'price': 'Цена',
            'quantity': 'Количество',
        }

    def clean(self):
        cleaned_data = super().clean()
        description = cleaned_data.get("description")
        if description is not None and len(description) < 20:
            raise ValidationError({
                "description": "Описание не может быть менее 20 символов."
            })

        name = cleaned_data.get("name")
        if name == description:
            raise ValidationError(
                "Описание не должно быть идентично названию."
            )

        return cleaned_data


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        author = Author.objects.create(authorUser=user)
        common_users = Group.objects.get(name="authors")
        user.groups.add(common_users)

        subject = 'Добро пожаловать в наш интернет-магазин!'
        text = f'{user.username}, вы успешно зарегистрировались на сайте!'
        html = (
            f'<b>{user.username}</b>, вы успешно зарегистрировались на '
            f'<a href="http://127.0.0.1:8000/products">сайте</a>!'
        )
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        return user

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Ваш отклик',
        }
