from django.db.models import Prefetch, Q
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from product.models import Category, SubCategory
from product.serializers import CategorySerializer, SubCategorySerializer
from utils.extensions.permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

