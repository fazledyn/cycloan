from django.urls import path
from. import views

urlpatterns = [
    path('',   views.LoginView.as_view(),   name='login-view'),
    path('email-verification/<str:verification_token>', views.EmailVerificationView.as_view(), name='email-verification-view'),
]