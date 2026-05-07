# apps/orders/urls.py

from django.urls import path
from .views import (
    OrderCreateView,
    OrderListView,
    OrderAllListView,
    OrderDetailView,
    OrderStatusUpdateView
)

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('', OrderListView.as_view(), name='order-list'),
    path('all/', OrderAllListView.as_view(), name='order-list-all'),
    path('<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]