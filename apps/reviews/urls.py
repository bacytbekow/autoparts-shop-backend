# apps/reviews/urls.py

from django.urls import path
from .views import (
    ReviewCreateView,
    ReviewListView,

    ReviewDetailView,
    ReviewModerateView
)

urlpatterns = [
    path('create/', ReviewCreateView.as_view(), name='review-create'),
    path('product/<int:product_id>/', ReviewListView.as_view(), name='review-list'),
    path('<int:id>/', ReviewDetailView.as_view(), name='review-detail'),
    path('<int:review_id>/moderate/', ReviewModerateView.as_view(), name='review-moderate'),
]