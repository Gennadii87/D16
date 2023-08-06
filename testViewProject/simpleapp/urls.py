import os
from django.urls import path

from .views import *


urlpatterns = [
   path('', ProductsList.as_view(), name='product_list'),
   path('<int:pk>',ProductDetail.as_view(), name='product_detail'),
   path('create/', ProductCreate.as_view(), name='product_create'),
   path('<int:pk>/update/', ProductUpdate.as_view(), name='product_update'),
   path('<int:pk>/delete/', ProductDelete.as_view(), name='product_delete'),
   path('subscriptions/', subscriptions, name='subscriptions'),
   path('comments/', comments, name='comments'),
   path('comments/<int:comment_id>/accept/', accept_comment, name='accept_comment'),
   path('comments/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
]