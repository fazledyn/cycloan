from django.urls import path
from core.views import insert_admin

urlpatterns = [
    path('login/', insert_admin, name='login'),
]