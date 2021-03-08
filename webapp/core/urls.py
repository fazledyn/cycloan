from django.urls import path
from . import views


urlpatterns = [
    # core view handlers
    path('',                                            views.IndexView.as_view(),              name='index-view'),
    path('trip-feedback/<int:trip_id>',                 views.TripFeedbackView.as_view(),       name='trip-feedback-view'),
    path('email-verification/<str:verification_token>', views.EmailVerificationView.as_view(),  name='email-verification-view'),

    # http error handlers
    path('403/',        views.Http403View.as_view(),        name='http-403-view'),
    path('404/',        views.Http404View.as_view(),        name='http-404-view'),
]
