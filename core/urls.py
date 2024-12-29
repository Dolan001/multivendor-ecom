from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet  # fcm urls
from rest_framework.routers import DefaultRouter

# fcm push notifications urls
router = DefaultRouter()
router.register(r"api/devices", FCMDeviceAuthorizedViewSet, basename="fcm")

swagger_urlpatterns = [
    path("api/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentications.urls")),
    # app urls
    path("api/shop/", include("product.urls")),
    path("api/shopping/", include("order.urls")),
    # # path("api/options/", include("options.urls")),
    # path("api/support/", include("support.urls")),
    # path("api/dashboard/", include("dashboard.urls")),
    # path("api/promo/", include("promotions.urls")),
]
# serving media and static files
media_url = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(
        r"^tinystatic/(?P<path>.*)$", serve, {"document_root": settings.TINYMCE_URL}
    ),
]

fcm_urls = [
    # path('api/devices/', FCMDeviceAuthorizedViewSet.as_view(), name='create_fcm_device'),
]
# serving media and static files and swagger
urlpatterns += media_url
# urlpatterns += fcm_urls
urlpatterns += router.urls
if settings.DEBUG:
    urlpatterns += swagger_urlpatterns
    # if app is in debug mode enable django toolbar
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
