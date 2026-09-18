# apps/cars/urls.py
from django.urls import path
from .views import *

urlpatterns = [

    path('create/', CarCreateView.as_view(), name='car-create'),
    path('', CarListView.as_view(), name='car-list'),
    path('<int:id>/', CarDetailView.as_view(), name='car-detail'),


    path('makes/', CarMakesView.as_view(), name='car-makes'),
    path('models/', CarModelsView.as_view(), name='car-models'),
    path('years/', CarYearsView.as_view(), name='car-years'),
]