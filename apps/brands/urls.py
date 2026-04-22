
from django.urls import path
from .views import BrandListView, BrandCreateView,BrandDetailView

urlpatterns = [
    path('', BrandListView.as_view(), name='brand-list'),
    path('create/', BrandCreateView.as_view(), name='brand-create'),
    path('<int:id>/', BrandDetailView.as_view(), name='brand-detail'),
]