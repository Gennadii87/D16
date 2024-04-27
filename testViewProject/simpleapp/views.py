import os
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Max
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404

from .models import *
from datetime import datetime
from .filters import ProductFilter, CommentFilterForm
from .forms import ProductForm, CommentForm


class ProductsList(ListView):
    model = Product
    ordering = 'name'
    template_name = 'products.html'
    context_object_name = 'products'
    paginate_by = 4  # вот так мы можем указать количество записей на странице
    ordering = '-created_at'# сортировка по дате создания поста объявления

    def get_queryset(self):

        # Получаем обычный запрос
        queryset = super().get_queryset()
        self.filterset = ProductFilter(self.request.GET, queryset)
        return self.filterset.qs.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now()
        context['next_sale'] = None
        context['filterset'] = self.filterset
        return context

        for product in context['products']:
            product.created_at = product.created_at.strftime('%Y-%m-%d %H:%M:%S')


class ProductDetail(DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(product=self.object).all()
        context['time_now'] = datetime.now()
        if self.request.user.is_authenticated:  # Проверяем, авторизован ли пользователь
            context['form'] = CommentForm()  # Если да, добавляем форму в контекст
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = self.object
            comment.save()
            return redirect('product_detail', pk=self.object.pk)


# Добавляем новое представление для создания товаров.
class ProductCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('simpleapp.add_product',)
    form_class = ProductForm
    model = Product
    template_name = 'product_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
        post.save()
        return super().form_valid(form)


class ProductUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('simpleapp.change_product',)
    form_class = ProductForm
    model = Product
    template_name = 'product_edit.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Проверяем, является ли текущий пользователь автором этого продукта
        if request.user != self.object.author.authorUser:
            # Если пользователь не автор, перенаправляем его на другую страницу (например, на страницу продуктов)
            return redirect('product_list')

        return super().dispatch(request, *args, **kwargs)

# Представление удаляющее товар.
class ProductDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('simpleapp.delete_product',)
    model = Product
    template_name = 'product_delete.html'
    success_url = reverse_lazy('product_list')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Проверяем, является ли текущий пользователь автором этого продукта
        if request.user != self.object.author.authorUser:
            # Если пользователь не автор, перенаправляем его на другую страницу (например, на страницу продуктов)
            return redirect('product_list')

        return super().dispatch(request, *args, **kwargs)


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )

def error_404(request, exception):
    return render(request, '404.html', status=404)


@login_required
def comments(request):
    # Получаем все продукты, созданные текущим пользователем (автором)
    products = Product.objects.filter(author=request.user.author)

    # Получаем все комментарии, связанные с этими продуктами, а также аннотируем максимальную дату создания отклика
    comments = Comment.objects.filter(product__in=products) \
                     .annotate(last_comment_date=Max('created_at')) \
                     .order_by('-last_comment_date')

    # Обработка фильтрации
    form = CommentFilterForm(request.GET)  # Передаем данные из запроса в форму

    if form.is_valid():
        product = form.cleaned_data['product']
        if product:
            comments = comments.filter(product=product)
    else:
        comments = comments.filter(product__author__authorUser=request.user)

    return render(request, 'comments_page.html', {'comments': comments, 'form': form})


@login_required
def accept_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Проверка, что текущий пользователь является автором продукта
    if request.user == comment.product.author.authorUser:
        comment.accepted = True
        comment.save()

    return redirect('comments')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Проверка, что текущий пользователь является автором продукта
    if request.user == comment.product.author.authorUser:
        comment.delete()

    return redirect('comments')
