from django.urls import path
from . import views


urlpatterns = [
    path('c/<int:customer_id>',    views.CustomerPublicView.as_view(),     name='customer-public-view'),
    path('o/<int:owner_id>',       views.OwnerPublicView.as_view(),        name='owner-public-view'),
    path('trip/<int:trip_id>',      views.TripDetailsView.as_view(),        name='trip-details-view'),
]