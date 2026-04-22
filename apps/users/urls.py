from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='customer-register'),
    # path('profile/', ProfileView.as_view(), name='profile'),


    path('admins/', AdminListView.as_view(), name='admin-list'),
    path('admins/create/', CreateAdminView.as_view(), name='create-admin'),
    path('admins/<int:id>/', AdminDetailView.as_view(), name='admin-detail'),


    path('managers/', ManagerListView.as_view(), name='manager-list'),
    path('managers/create/', CreateManagerView.as_view(), name='create-manager'),
    path('managers/<int:id>/', ManagerDetailView.as_view(), name='manager-detail'),


    path('content/', ContentListView.as_view(), name='content-list'),
    path('content/create/', CreateContentView.as_view(), name='create-content'),
    path('content/<int:id>/', ContentDetailView.as_view(), name='content-detail'),
]