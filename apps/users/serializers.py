from rest_framework import serializers
from .models import User



# ========== ДЛЯ АДМИНОВ (с аудитом) =====
class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Для админа и суперадмина (полная информация с аудитом)"""
    updated_by_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 'city', 'role',
                  'is_staff', 'date_joined', 'updated_at', 'updated_by_info']
        read_only_fields = ['id', 'date_joined', 'updated_at', 'updated_by_info']

    def get_updated_by_info(self, obj):
        if obj.updated_by:
            return {
                'id': obj.updated_by.id,
                'username': obj.updated_by.username,
            }
        return None



# ========== ДЛЯ ВСЕХ ОСТАЛЬНЫХ ==========
class BaseUserDetailSerializer(serializers.ModelSerializer):
    """Базовый сериализатор (без аудита) - для менеджеров, контента, покупателей"""
    class Meta:
        model = User
        fields = ['id',  'email', 'first_name', 'last_name', 'phone', 'address', 'city', 'date_joined']
        read_only_fields = ['id', 'username', 'email', 'date_joined']



# ========== ДЛЯ СПИСКОВ =================

class UserListSerializer(serializers.ModelSerializer):
    """Универсальный список для всех пользователей"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_active', 'date_joined']



# ========== ДЛЯ СОЗДАНИЯ =================
class AdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone', 'address', 'city']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', '')
        )
        user.role = 'admin'
        user.is_staff = True
        user.save()
        return user
class ManagerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone', 'address', 'city']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            address=validated_data['address'],
            city=validated_data['city']
        )
        user.role = 'manager'
        user.is_staff = True
        user.save()
        return user
class ContentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone', 'address', 'city']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            address=validated_data['address'],
            city=validated_data['city']
        )
        user.role = 'content'
        user.is_staff = True
        user.save()
        return user
class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'phone', 'first_name', 'last_name', 'address', 'city']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', '')
        )
        user.role = 'customer'
        user.is_staff = False
        user.save()
        return user



# ========== ДЛЯ ПРОФИЛЯ =================
# apps/users/serializers.py

class ProfileSerializer(BaseUserDetailSerializer):
    class Meta(BaseUserDetailSerializer.Meta):
        fields = BaseUserDetailSerializer.Meta.fields + ['role']
        read_only_fields = ['id', 'email', 'date_joined', 'role']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Только суперпользователя превращаем в superadmin
        if instance.is_superuser:
            data['role'] = 'superadmin'
        # Админ, менеджер, контент остаются как есть
        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля (email можно менять, username нельзя)"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'city']

    def validate_email(self, value):
        """Проверка, что email уникальный"""
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def update(self, instance, validated_data):
        # Обновляем только разрешенные поля
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.save()
        return instance