from django.urls import path
from rest_framework.routers import DefaultRouter
from product.views import (
    CategoryViewSet, SubCategoryViewSet, VendorViewSet, ProductViewSet, AnalyticsAPIView
)


router = DefaultRouter()

router.register('category', CategoryViewSet, basename='category')
router.register('sub-category', SubCategoryViewSet, basename='sub_category')
router.register('vendor', VendorViewSet, basename='vendor')
router.register('products', ProductViewSet, basename='product')
urlpatterns = [
    path('analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    path('vendor-analytics/', VendorViewSet.as_view({'get': 'vendor_analytics'}), name='vendor_analytics'),
] + router.urls
