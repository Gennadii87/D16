import os
from django.contrib import admin
from django.db import models
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _

from .models import *

admin.site.register(Category)
admin.site.register(Author)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_name', 'text', 'created_at', 'accepted')
    list_filter = ('created_at', 'accepted')
    search_fields = ('id', 'user__username', 'product__name', 'text')

    def product_name(self, obj):
        return obj.product.name

    product_name.short_description = 'Название продукта'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'price', 'category', 'created_at', 'author']
    list_display_links = ['name', 'category']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category']
    list_display_links = ['user', 'category']


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

