# apps/products/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),  # ✅ slug аркылуу
    path('<int:id>/', ProductDetailView.as_view(), name='product-detail-id'),  # ✅ id аркылуу да (опционал)
]