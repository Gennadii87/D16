from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=Product)
def product_created(instance, created, **kwargs):
    if not created:
        return

    emails = User.objects.filter(
        subscriptions__category=instance.category
    ).values_list('email', flat=True)
    subject = f'Новый товар в категории {instance.category}'
    text_content = (
        f'Товар: {instance.name}\n'
        f'Цена: {instance.price}\n\n'
        f'Ссылка на товар: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )
    html_content = (
        f'Товар: {instance.name}<br>'
        f'Цена: {instance.price}<br><br>'
        f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
        f'Ссылка на товар</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        subject = f'Новый отклик на ваш продукт {instance.product.name}'
        message = f'Вы получили новый отклик на ваш продукт {instance.product.name}.'
        recipient_list = [instance.product.author.authorUser.email]

        # Опционально, вы можете использовать шаблон письма для улучшения форматирования
        context = {
            'product_name': instance.product.name,
            'comment_author': instance.user.username,
        }
        html_message = render_to_string('email/comment_notification.html', context)
        plain_message = strip_tags(html_message)

        send_mail(subject, plain_message, None, recipient_list, html_message=html_message)


@receiver(post_save, sender=Comment)
def send_comment_accepted_notification(sender, instance, **kwargs):
    comment = instance
    user = comment.user
    product = comment.product

    if comment.accepted:
        subject = 'Ваш отклик принят!'
        context = {'user': user, 'product': product}
        html_message = render_to_string('email/comment_accepted_notification.html', context)
        plain_message = strip_tags(html_message)

        recipient_list = [user.email]
        send_mail(subject, plain_message, None, recipient_list, html_message=html_message)




@receiver(post_save, sender=User)
def create_author(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(authorUser=instance)

@receiver(post_save, sender=User)
def save_author(sender, instance, **kwargs):
    instance.author.save()