from django.urls import path
from portal import views

app_name = 'portal'

urlpatterns = [
    path('login/', views.portal_login, name='login'),
    path('logout/', views.portal_logout, name='logout'),
    path('', views.portal_dashboard, name='dashboard'),
]