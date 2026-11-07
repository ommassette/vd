from django.urls import include, path
from app.admin import admin_site

urlpatterns = [
    path('siri/', admin_site.urls),
    path('', include('app.urls')),
]