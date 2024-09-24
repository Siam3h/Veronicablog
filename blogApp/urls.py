from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# from django.urls import re_path as url
# from django.conf import settings
# from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', include('home.urls')),
    path('payments/', include("payments.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
