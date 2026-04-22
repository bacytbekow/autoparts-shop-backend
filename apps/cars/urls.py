# apps/cars/urls.py
from django.urls import path
from .views import *

urlpatterns = [

    path('create/', CarCreateView.as_view(), name='car-create'),
    path('', CarListView.as_view(), name='car-list'),
    path('<int:id>/', CarDetailView.as_view(), name='car-detail'),
]