from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from projects.views import HomePageView

urlpatterns = [
    path('users/', include('django.contrib.auth.urls')),
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="landing"),
    path("projects/", include("projects.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
