from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from .permissions import *

class ProfileView(generics.RetrieveAPIView):
    """Профиль текущего авторизованного пользователя"""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# Админстраторов
class CreateAdminView(generics.CreateAPIView):
    serializer_class = AdminCreateSerializer
    permission_classes = [permissions.IsAuthenticated, OnlySuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Администратор "{serializer.instance.username}" успешно создан',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
class AdminListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, OnlySuperAdmin]  # ← только суперадмин!

    def get_queryset(self):
        # Только суперадмин имеет доступ, возвращаем всех админов
        return User.objects.filter(role='admin')
class AdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SeeOwnOrAllByAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.filter(role='admin')
        if self.request.user.role == 'admin':
            return User.objects.filter(id=self.request.user.id, role='admin')
        return User.objects.none()

    def get_serializer_class(self):
        if self.request.user.role == 'admin' and not self.request.user.is_superuser:
            return BaseUserDetailSerializer
        return AdminUserDetailSerializer

    def update(self, request, *args, **kwargs):
        """Обновление администратора с сообщением"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response({
            'message': f'Администратор "{instance.username}" успешно обновлён',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = User.objects.get(id=kwargs.get('id'), role='admin')
        except User.DoesNotExist:
            return Response(
                {'error': 'Администратор не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_user = request.user
        username = instance.username

        if current_user.role == 'admin' and not current_user.is_superuser:
            if instance.id == current_user.id:
                return Response(
                    {'error': 'Вы не можете удалить самого себя'},
                    status=status.HTTP_403_FORBIDDEN
                )
            return Response(
                {'error': 'Только суперадмин может удалять администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.delete()
        return Response(
            {'message': f'Администратор "{username}" успешно удалён'},
            status=status.HTTP_200_OK
        )


# Менеджеров
class CreateManagerView(generics.CreateAPIView):
    serializer_class = ManagerCreateSerializer
    permission_classes = [permissions.IsAuthenticated, AdminOrSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Менеджер "{serializer.instance.username}" успешно создан',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
class ManagerListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, AdminOrSuperAdmin]  # ← админ и суперадмин

    def get_queryset(self):
        return User.objects.filter(role='manager')
class ManagerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SeeOwnOrAllByAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(role='manager')

    def get_serializer_class(self):
        if self.request.user.role == 'manager' and not self.request.user.is_superuser:
            return BaseUserDetailSerializer
        return AdminUserDetailSerializer

    def update(self, request, *args, **kwargs):
        """Обновление менеджера с сообщением"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response({
            'message': f'Менеджер "{instance.username}" успешно обновлён',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = User.objects.get(id=kwargs.get('id'), role='manager')
        except User.DoesNotExist:
            return Response(
                {'error': 'Менеджер не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_user = request.user
        username = instance.username

        if instance.id == current_user.id:
            return Response(
                {'error': 'Вы не можете удалить самого себя'},
                status=status.HTTP_403_FORBIDDEN
            )

        if current_user.role not in ['admin'] and not current_user.is_superuser:
            return Response(
                {'error': 'Только администраторы могут удалять менеджеров'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.delete()
        return Response(
            {'message': f'Менеджер "{username}" успешно удалён'},
            status=status.HTTP_200_OK
        )


# Контент менеджер
class CreateContentView(generics.CreateAPIView):
    serializer_class = ContentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, AdminOrSuperAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'message': f'Контент-менеджер "{serializer.instance.username}" успешно создан',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
class ContentListView(generics.ListAPIView):
    serializer_class = UserListSerializer  # ← используем общий UserListSerializer
    permission_classes = [permissions.IsAuthenticated, AdminOrSuperAdmin]  # ← только админ и суперадмин

    def get_queryset(self):
        return User.objects.filter(role='content')
class ContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SeeOwnOrAllByAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(role='content')

    def get_serializer_class(self):
        if self.request.user.role == 'content' and not self.request.user.is_superuser:
            return BaseUserDetailSerializer
        return AdminUserDetailSerializer

    def update(self, request, *args, **kwargs):
        """Обновление контент-менеджера с сообщением"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response({
            'message': f'Контент-менеджер "{instance.username}" успешно обновлён',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = User.objects.get(id=kwargs.get('id'), role='content')
        except User.DoesNotExist:
            return Response(
                {'error': 'Контент-менеджер не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_user = request.user
        username = instance.username

        if instance.id == current_user.id:
            return Response(
                {'error': 'Вы не можете удалить самого себя'},
                status=status.HTTP_403_FORBIDDEN
            )

        if current_user.role not in ['admin'] and not current_user.is_superuser:
            return Response(
                {'error': 'Только администраторы могут удалять контент-менеджеров'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.delete()
        return Response(
            {'message': f'Контент-менеджер "{username}" успешно удалён'},
            status=status.HTTP_200_OK
        )


# ПОКУПАТЕЛЬ
class CustomerRegisterView(generics.CreateAPIView):
    serializer_class = CustomerRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Вы успешно зарегистрировались!',  # ← добавил
            'user': ProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
class CustomerListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, ManagerAdminOrSuperAdmin]  # менеджер, админ, суперадмин

    def get_queryset(self):
        return User.objects.filter(role='customer')
class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, SeeOwnOrAllByAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(role='customer')

    def get_serializer_class(self):
        if self.request.user.role == 'customer' and not self.request.user.is_superuser:
            return BaseUserDetailSerializer
        return AdminUserDetailSerializer

    def update(self, request, *args, **kwargs):
        """Обновление покупателя с сообщением"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return Response({
            'message': f'Покупатель "{instance.username}" успешно обновлён',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = User.objects.get(id=kwargs.get('id'), role='customer')
        except User.DoesNotExist:
            return Response(
                {'error': 'Покупатель не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_user = request.user
        username = instance.username

        if instance.id == current_user.id:
            return Response(
                {'error': 'Вы не можете удалить самого себя'},
                status=status.HTTP_403_FORBIDDEN
            )

        if current_user.role not in ['admin'] and not current_user.is_superuser:
            return Response(
                {'error': 'Только администраторы могут удалять покупателей'},
                status=status.HTTP_403_FORBIDDEN
            )

        instance.delete()
        return Response(
            {'message': f'Покупатель "{username}" успешно удалён'},
            status=status.HTTP_200_OK
        )
