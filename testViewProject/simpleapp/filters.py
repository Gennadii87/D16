from django_filters import FilterSet, filters
from django import forms
from .models import Product, Category


class ProductFilter(FilterSet):
    class Meta:
       model = Product
       fields = {
           # поиск по названию
           'name': ['icontains'],
           # количество товаров должно быть больше или равно
           'quantity': ['gt'],
           'price': [
               'lt',  # цена должна быть меньше или равна указанной
               'gt',  # цена должна быть больше или равна указанной
           ],
       }
       labels = {
           'name': 'Наименование',
           'quantity': 'Количество',
           'price__lt': 'Максимальная цена',
           'price__gt': 'Минимальная цена',
       }


class ProductFilter(FilterSet):
    name = filters.CharFilter(field_name='name', label='Наименование',)
    price__lt = filters.NumberFilter(field_name='price', label='Максимальная цена', lookup_expr='lte')
    price__gt = filters.NumberFilter(field_name='price', label='Минимальная цена', lookup_expr='gte')
    quantity = filters.NumberFilter(field_name='quantity', label='Количество', lookup_expr='gt')
    category = filters.ChoiceFilter(field_name='category__name', label='Категория', choices=Category.objects.values_list('name', 'name'))

    class Meta:
        model = Product
        fields = []

class CommentFilterForm(forms.Form):
    product = forms.ModelChoiceField(label='Продукт', queryset=Product.objects.all(), empty_label='Все продукты', required=False)

