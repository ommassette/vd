from django.contrib.auth import views as auth_views
from django.urls import path
from app.admin import admin_site
from . import views

app_name = 'portal'

urlpatterns = [
    path('siri/', admin_site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.portal_dashboard, name='dashboard'),
]