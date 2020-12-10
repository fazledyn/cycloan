from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('',            include('core.urls')),
    path('owner/',      include('owner.urls')),
    path('customer/',   include('customer.urls')),
    path('user/',       include('user.urls')),
    path('cycle/',      include('cycle.urls')),
    path('admin/',      include('admin.urls')),
]
