from django.urls import path
from . import views

urlpatterns = [
    path('login/',      views.CustomerLoginView.as_view(),      name='customer-login-view'),
    path('register/',   views.CustomerRegisterView.as_view(),   name='customer-register-view'),
    path('dashboard/',  views.CustomerDashboardView.as_view(),  name='customer-dashboard-view'),
    path('logout/',     views.CustomerLogoutView.as_view(),     name='customer-logout-view'),
    path('profile/',    views.CustomerProfileView.as_view(),    name='customer-profile-view'),
]
