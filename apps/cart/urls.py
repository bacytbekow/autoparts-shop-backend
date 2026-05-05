# apps/cart/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', CartAddView.as_view(), name='cart-add'),
    path('update/<int:item_id>/', CartUpdateView.as_view(), name='cart-update'),
    path('remove/<int:item_id>/', CartRemoveView.as_view(), name='cart-remove'),
    path('clear/', CartClearView.as_view(), name='cart-clear'),

]