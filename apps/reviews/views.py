# apps/reviews/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from .permissions import IsOwnerOrAdmin, IsAdminOrContent


class ReviewCreateView(generics.CreateAPIView):
    """Создание отзыва"""
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        user = self.request.user

        if user.is_authenticated and (user.role in ['admin', 'content'] or user.is_superuser):
            return Review.objects.filter(product_id=product_id)

        return Review.objects.filter(product_id=product_id, status='approved')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        # При обновлении сбрасываем статус на модерацию
        serializer.save(status='pending')


class ReviewModerateView(APIView):
    """Модерация отзыва (админ/контент)"""
    permission_classes = [permissions.IsAuthenticated, IsAdminOrContent]

    def patch(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Отзыв не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        status_new = request.data.get('status')
        if status_new not in ['pending', 'approved', 'rejected']:
            return Response(
                {'error': 'Неверный статус. Допустимые: pending, approved, rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        review.status = status_new
        review.save()

        return Response({
            'message': f'Статус отзыва изменён на "{review.get_status_display()}"',
            'review': ReviewSerializer(review).data
        }, status=status.HTTP_200_OK)