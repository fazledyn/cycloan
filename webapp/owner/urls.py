from django.urls import path
from . import views

urlpatterns = [
    path('',            views.OwnerLandingView.as_view(),       name='owner-landing-view'),
    path('cycle/',      views.OwnerCycleView.as_view(),         name='owner-cycle-view'),
    path('login/',      views.OwnerLoginView.as_view(),         name='owner-login-view'),
    path('register/',   views.OwnerRegisterView.as_view(),      name='owner-register-view'),
    path('dashboard/',  views.OwnerDashboardView.as_view(),     name='owner-dashboard-view'),
    path('logout/',     views.OwnerLogoutView.as_view(),        name='owner-logout-view'),
    path('profile/',    views.OwnerProfileView.as_view(),       name='owner-profile-view'),
    path('trip/',       views.OwnerTripHistoryView.as_view(),   name='owner-trip-history-view'),
]
