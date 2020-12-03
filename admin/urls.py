from django.urls import path
from . import views

urlpatterns = [
    path('login/',          views.AdminLoginView.as_view(),         name='admin-login-view'),
    path('dashboard/',      views.AdminDashboardView.as_view(),     name='admin-dashboard-view'),
    path('cycle_list/',     views.ShowCycleListView.as_view(),      name='admin-cycle-list-view'),
    path('owner_list/',     views.ShowOwnerListView.as_view(),      name='admin-owner-list-view'),
    path('customer_list/',  views.ShowCustomerListView.as_view(),   name='admin-customer-list-view'),
    path('register/',       views.AdminRegisterView.as_view(),      name='admin-register-view'),
]