# contact_search/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('search/', include('search_app.urls')),
    path('', include('search_app.urls')),  # 👈 ADD THIS LINE - root redirect
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
