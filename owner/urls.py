from django.urls import path
from . import views

urlpatterns = [
    path('login/',      views.OwnerLoginView.as_view(),     name='owner-login-view'),
    path('register/',   views.OwnerRegisterView.as_view(),  name='owner-register-view'),
    path('dashboard/',  views.OwnerDashboardView.as_view(), name='owner-dashboard-view'),
    path('logout/',     views.OwnerLogoutView.as_view(),    name='owner-logout-view'),
]
