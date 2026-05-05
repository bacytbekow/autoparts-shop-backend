# apps/product_images/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('product/<int:product_id>/', ProductImageListView.as_view(), name='product-image-list'),
    path('create/', ProductImageCreateView.as_view(), name='product-image-create'),
    path('<int:id>/', ProductImageDetailView.as_view(), name='product-image-detail'),
]