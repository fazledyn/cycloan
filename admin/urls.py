from django.urls import path
from . import views

urlpatterns = [
    path('trip/',       views.TripListView.as_view(),       name='trip-list-view'),
    path('owner/',      views.OwnerListView.as_view(),      name='owner-list-view'),
    path('cycle/',      views.CycleListView.as_view(),      name='cycle-list-view'),
    path('customer/',   views.CustomerListView.as_view(),   name='customer-list-view'),
    
    path('dashboard/',  views.AdminDashboardView.as_view(), name='admin-dashboard-view'),
    path('login/',      views.AdminLoginView.as_view(),     name='admin-login-view'),
    path('logout/',     views.AdminLogoutView.as_view(),     name='admin-logout-view'),
    path('register/',   views.AdminRegisterView.as_view(),  name='admin-register-view'),
]