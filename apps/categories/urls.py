from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CategoryCreateView.as_view(), name='category-create'),
    path('', CategoryListView.as_view(), name='category-list'),

    path('<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
]