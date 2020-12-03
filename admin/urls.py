from django.urls import path
from . import views

urlpatterns = [
    path('login/',      views.AdminLoginView.as_view(),     name='admin-login-view'),
    path('dashboard/',  views.AdminDashboardView.as_view(), name='admin-dashboard-view'),
]