from django.urls import path
from. import views

urlpatterns = [
    path('login/',          views.LoginView.as_view(),          name='login-view'),
    path('customer-login/', views.CustomerLoginView.as_view(),  name='customer-login-view'),
    path('owner-login/',    views.OwnerLoginView.as_view(),     name='owner-login-view'),
    path('owner-signup/', views.OwnerSignup.as_view(), name='owner-signup'),
]