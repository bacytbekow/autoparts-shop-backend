# apps/products/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]