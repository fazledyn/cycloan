from django.urls import path
from. import views

urlpatterns = [
    path('',   views.LoginView.as_view(),   name='login-view'),
    path('login_admin/',   views.LoginViewForAdmin.as_view(),   name='login-view-for-admin'),
    path('email-verification/<str:verification_token>', views.EmailVerificationView.as_view(), name='email-verification-view'),
    path('trip-feedback/<int:trip_id>',     views.TripFeedbackView.as_view(),         name='trip-feedback-view'),
]